"""Convert Keep geo-point clocks into Unix seconds.

Keep's ``startTime`` is Unix time in milliseconds. Each point is not:

- older exports store ``timestamp`` as elapsed deciseconds (tenths of a second)
- newer exports store ``timestamp`` as an absolute decisecond clock
- points without ``timestamp`` carry ``unixTimestamp``, which is Unix milliseconds

Treating a millisecond clock as deciseconds (divide by 10) lands in year ~7500.
Zeroing ``startTime`` for the whole track because the first point looks
"absolute" then turns every later delta into a 1970 timestamp.
"""

import re
from datetime import UTC, datetime

# 100 hours in deciseconds. A real activity is shorter than this, so a larger
# value is an absolute clock rather than an elapsed time.
TIMESTAMP_THRESHOLD_IN_DECISECOND = 3_600_000

# Unix milliseconds from 1973 onward. Absolute deciseconds stay below this
# until year 2286, so the two absolute forms do not overlap.
UNIX_MILLISECONDS_MIN = 100_000_000_000

_TIME_RE = re.compile(r"<time>([^<]+)</time>")


def keep_point_epoch_seconds(timestamp, start_time_ms):
    """Return Unix seconds for one Keep point.

    ``start_time_ms`` is the activity ``startTime`` (Unix milliseconds).
    ``timestamp`` is whatever ended up on the point: a delta in deciseconds,
    an absolute decisecond clock, or Unix milliseconds.
    """
    ts = int(timestamp or 0)
    start_ms = int(start_time_ms or 0)
    if ts >= UNIX_MILLISECONDS_MIN:
        return ts // 1000
    if ts > TIMESTAMP_THRESHOLD_IN_DECISECOND:
        return ts // 10
    return start_ms // 1000 + ts // 10


def keep_point_delta_deciseconds(timestamp, start_time_ms):
    """Elapsed deciseconds from ``startTime``, for matching heart-rate samples."""
    ts = int(timestamp or 0)
    start_ms = int(start_time_ms or 0)
    if ts >= UNIX_MILLISECONDS_MIN:
        return (ts - start_ms) // 100
    if ts > TIMESTAMP_THRESHOLD_IN_DECISECOND:
        return ts - start_ms // 100
    return ts


def _format_gpx_time(epoch_seconds):
    moment = datetime.fromtimestamp(epoch_seconds, tz=UTC)
    millis = moment.microsecond // 1000
    if millis:
        return moment.strftime("%Y-%m-%dT%H:%M:%S") + f".{millis:03d}Z"
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def repair_keep_gpx_times(xml_text):
    """Rewrite one GPX produced by the old millisecond/decisecond mix.

    The broken shape is a single leading ``<time>`` in year 3000+ (Unix
    milliseconds divided by 10) followed only by 1970 timestamps (elapsed
    seconds, because ``startTime`` was discarded). Returns the repaired XML,
    or ``None`` when the file does not have that shape.
    """
    matches = list(_TIME_RE.finditer(xml_text))
    if len(matches) < 2:
        return None
    moments = [datetime.fromisoformat(match.group(1)) for match in matches]
    if moments[0].year < 3000:
        return None
    if any(moment.year >= 3000 for moment in moments[1:]):
        return None
    if any(moment.year >= 1990 for moment in moments[1:]):
        return None

    # stored_seconds = unix_ms // 10, so unix seconds = stored_seconds / 100.
    start_seconds = moments[0].timestamp() / 100
    repaired = [_format_gpx_time(start_seconds)]
    for moment in moments[1:]:
        repaired.append(_format_gpx_time(start_seconds + moment.timestamp()))

    index = 0

    def _replace(_match):
        nonlocal index
        value = repaired[index]
        index += 1
        return f"<time>{value}</time>"

    return _TIME_RE.sub(_replace, xml_text)
