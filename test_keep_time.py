"""Keep point clocks: milliseconds must not be read as deciseconds."""

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "run_page"))

from keep_time import (  # noqa: E402
    keep_point_delta_deciseconds,
    keep_point_epoch_seconds,
    repair_keep_gpx_times,
)

# 2025-07-21 11:03:46 UTC
START_MS = 1_753_095_826_000


def _utc(epoch_seconds):
    return datetime.fromtimestamp(epoch_seconds, tz=UTC)


def test_elapsed_deciseconds_are_added_to_start():
    # 425 deciseconds = 42 seconds
    moment = _utc(keep_point_epoch_seconds(425, START_MS))
    assert moment == datetime(2025, 7, 21, 11, 4, 28, tzinfo=UTC)


def test_unix_milliseconds_stay_in_the_activity_year():
    unix_ms = 1_753_096_298_720
    # The old formula (ms // 10) is what produced years like 7525.
    assert _utc(unix_ms // 10).year == 7525
    moment = _utc(keep_point_epoch_seconds(unix_ms, START_MS))
    assert moment == datetime(2025, 7, 21, 11, 11, 38, tzinfo=UTC)


def test_absolute_millisecond_point_does_not_drop_later_deltas():
    unix_ms = 1_753_096_298_720
    later = _utc(keep_point_epoch_seconds(100, START_MS))
    assert later == datetime(2025, 7, 21, 11, 3, 56, tzinfo=UTC)
    assert _utc(keep_point_epoch_seconds(unix_ms, START_MS)).year == 2025


def test_absolute_deciseconds_are_not_added_to_start():
    start_sec = START_MS // 1000
    absolute_ds = start_sec * 10 + 50  # +5 seconds
    assert keep_point_epoch_seconds(absolute_ds, START_MS) == start_sec + 5


def test_heart_rate_delta_for_unix_milliseconds():
    unix_ms = START_MS + 12_500  # 12.5 seconds → 125 deciseconds
    assert keep_point_delta_deciseconds(unix_ms, START_MS) == 125
    assert keep_point_delta_deciseconds(125, START_MS) == 125


def test_repair_rewrites_the_7559_pattern():
    # 7525-05-05T15:24:32Z is 175309629872 seconds, /100 → 2025-07-21 11:11:38.720Z
    xml = """<gpx>
      <trkpt lat="1" lon="2"><time>7525-05-05T15:24:32Z</time></trkpt>
      <trkpt lat="1" lon="2"><time>1970-01-01T00:00:01Z</time></trkpt>
      <trkpt lat="1" lon="2"><time>1970-01-01T00:00:02Z</time></trkpt>
    </gpx>
    """
    repaired = repair_keep_gpx_times(xml)
    assert repaired is not None
    assert "7525-" not in repaired
    assert "1970-" not in repaired
    assert "2025-07-21T11:11:38.720Z" in repaired
    assert "2025-07-21T11:11:39.720Z" in repaired
    assert "2025-07-21T11:11:40.720Z" in repaired


def test_repair_leaves_normal_gpx_alone():
    xml = "<time>2024-01-02T03:04:05Z</time><time>2024-01-02T03:04:06Z</time>"
    assert repair_keep_gpx_times(xml) is None
