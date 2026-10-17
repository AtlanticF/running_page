import datetime
import os
import sys

import arrow
import stravalib
from gpxtrackposter import track_loader
from polyline_processor import filter_out
from sqlalchemy import func
from synced_data_file_logger import save_synced_data_file_list

from .db import Activity, init_db, update_or_create_activity

IGNORE_BEFORE_SAVING = os.getenv(
    "IGNORE_BEFORE_SAVING",
    False,  # noqa: PLW1508
)


class Generator:
    def __init__(self, db_path):
        self.client = stravalib.Client()
        self.session = init_db(db_path)

        self.client_id = ""
        self.client_secret = ""
        self.refresh_token = ""
        self.only_run = False

    def set_strava_config(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    def check_access(self):
        response = self.client.refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
        )
        # Update the authdata object
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]

        self.client.access_token = response["access_token"]
        print("Access ok")

    def sync(self, force):
        """
        Sync activities means sync from strava
        TODO, better name later
        """
        self.check_access()

        print("Start syncing")
        if force:
            filters = {"before": datetime.datetime.now(datetime.UTC)}
        else:
            last_activity = self.session.query(func.max(Activity.start_date)).scalar()
            if last_activity:
                last_activity_date = arrow.get(last_activity)
                last_activity_date = last_activity_date.shift(days=-7)
                filters = {"after": last_activity_date.datetime}
            else:
                filters = {"before": datetime.datetime.now(datetime.UTC)}

        for activity in self.client.get_activities(**filters):
            if self.only_run and activity.type != "Run":
                continue
            if IGNORE_BEFORE_SAVING and activity.map and activity.map.summary_polyline:
                activity.map.summary_polyline = filter_out(
                    activity.map.summary_polyline
                )
            #  strava use total_elevation_gain as elevation_gain
            activity.elevation_gain = activity.total_elevation_gain
            activity.subtype = activity.type
            created = update_or_create_activity(self.session, activity)
            if created:
                sys.stdout.write("+")
            else:
                sys.stdout.write(".")
            sys.stdout.flush()
        self.session.commit()

    def sync_from_data_dir(
        self, data_dir, file_suffix="gpx", activity_title_dict=None, limit=None
    ):
        loader = track_loader.TrackLoader()
        tracks = loader.load_tracks(
            data_dir,
            file_suffix=file_suffix,
            activity_title_dict=activity_title_dict,
            limit=limit,
        )
        print(f"load {len(tracks)} tracks")
        if not tracks:
            print("No tracks found.")
            return

        synced_files = []
        total = len(tracks)

        for index, t in enumerate(tracks, start=1):
            fname = t.file_names[0] if t.file_names else ""
            print(f"save {index}/{total} {fname}", flush=True)
            # to_namedtuple may return None for tracks that were filtered/skipped
            nt = t.to_namedtuple(run_from=file_suffix)
            if nt is None:
                # t.to_namedtuple already logs a human-readable message when skipping,
                # record a short marker and continue without touching DB
                print(f"skip {index}/{total} {fname}", flush=True)
                sys.stdout.write("s")
                sys.stdout.flush()
                continue

            print(f"upsert {index}/{total} {fname} id={nt.id}", flush=True)
            created = update_or_create_activity(self.session, nt)
            print(
                f"upsert done {index}/{total} {fname} created={created}",
                flush=True,
            )
            if created:
                sys.stdout.write("+")
            else:
                sys.stdout.write(".")
            synced_files.extend(t.file_names)
            sys.stdout.flush()

        print(f"commit {len(synced_files)} files", flush=True)
        save_synced_data_file_list(synced_files)

        self.session.commit()
        print("commit done", flush=True)

    def sync_from_app(self, app_tracks):
        if not app_tracks:
            print("No tracks found.")
            return
        print("Syncing tracks '+' means new track '.' means update tracks")
        synced_files = []
        for t in app_tracks:
            created = update_or_create_activity(self.session, t)
            if created:
                sys.stdout.write("+")
            else:
                sys.stdout.write(".")
            if "file_names" in t:
                synced_files.extend(t.file_names)
            sys.stdout.flush()

        self.session.commit()

    def load(self):
        # if sub_type is not in the db, just add an empty string to it
        query = self.session.query(Activity).filter(Activity.distance > 0.1)
        if self.only_run:
            query = query.filter(Activity.type == "Run")

        activities = query.order_by(Activity.start_date_local)
        activity_list = []

        streak = 0
        last_date = None
        for activity in activities:
            # Determine running streak.
            date = datetime.datetime.strptime(  # noqa: DTZ007
                activity.start_date_local, "%Y-%m-%d %H:%M:%S"  # type: ignore
            ).date()
            if last_date is None:
                streak = 1
            elif date == last_date:
                pass
            elif date == last_date + datetime.timedelta(days=1):
                streak += 1
            else:
                assert date > last_date
                streak = 1
            activity.streak = streak  # type: ignore
            last_date = date
            exported_activity = activity.to_dict()
            if not IGNORE_BEFORE_SAVING:
                exported_activity["summary_polyline"] = filter_out(
                    exported_activity["summary_polyline"]
                )
            activity_list.append(exported_activity)

        self.session.commit()
        return activity_list

    def get_old_tracks_ids(self):
        try:
            activities = self.session.query(Activity).all()
            return [str(a.run_id) for a in activities]
        except Exception as e:  # noqa: BLE001
            # pass the error
            print(f"something wrong with {e!s}")
            return []

    def get_old_tracks_dates(self):
        try:
            activities = (
                self.session.query(Activity)
                .order_by(Activity.start_date_local.desc())
                .all()
            )
            return [str(a.start_date_local) for a in activities]
        except Exception as e:  # noqa: BLE001
            # pass the error
            print(f"something wrong with {e!s}")
            return []
