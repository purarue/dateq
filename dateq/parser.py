from __future__ import annotations

import sys
import re
import zoneinfo
from typing import TYPE_CHECKING
from datetime import datetime, timezone, timedelta

# from .log import logger

if TYPE_CHECKING:
    from dateparser import _Settings


# TODO: make this configurable?
DATEPARSER_SETTINGS: _Settings = {"DATE_ORDER": "YMD"}


def _parse_epoch_timestamps(
    date_val: int | float, /, *, parse_epoch_milliseconds: bool = False
) -> datetime | None:
    # also handles epoch timestamps as integers
    try:
        # convert to make sure its a valid datetime
        return datetime.fromtimestamp(date_val)
    except ValueError:
        pass

    if parse_epoch_milliseconds:
        try:
            return datetime.fromtimestamp(date_val / 1000)
        except ValueError:
            pass

    return None


def _parse_datetime(
    date_input: str | int | float, /, *, parse_epoch_milliseconds: bool = False
) -> datetime | None:
    if isinstance(date_input, (int, float)):
        return _parse_epoch_timestamps(
            date_input, parse_epoch_milliseconds=parse_epoch_milliseconds
        )

    # epoch timestamp, but a string
    if date_input.isdigit() or date_input.isdecimal():
        # also handles epoch timestamps as integers
        ds_float = float(date_input)
        return _parse_epoch_timestamps(
            ds_float, parse_epoch_milliseconds=parse_epoch_milliseconds
        )

    if date_input.strip() == "":
        return None
    elif date_input == "now":
        return datetime.now()

    try:
        # isoformat - default format when you call str() on datetime
        # this also parses dates like '2020-01-01'
        return datetime.fromisoformat(date_input)
    except ValueError:
        pass

    try:
        import dateparser
    except ImportError as ie:
        raise ImportError(
            f"'dateparser' not installed, install with '{sys.executable} -m pip install dateparser'"
        ) from ie

    # dateparser is a bit more lenient than the above, lets you type
    # all sorts of dates as inputs
    # https://github.com/scrapinghub/dateparser#how-to-use
    res: datetime | None = dateparser.parse(date_input, settings=DATEPARSER_SETTINGS)
    if res is not None:
        return res.astimezone()

    return None


def _handle_timezone(
    dt: datetime,
    /,
    *,
    tz: zoneinfo.ZoneInfo | timezone | None,
    convert_to_utc: bool = False,
    localize_datetime: bool = False,
) -> datetime:
    if convert_to_utc is True and localize_datetime is True:
        raise ValueError("convert_to_utc and localize_datetime are mutually exclusive")
    if convert_to_utc or localize_datetime:
        # if nothing set, use the passed timezone else get your own
        if dt.tzinfo is None:
            if tz is not None:
                # this just replaces the tzinfo with the one you specified,
                # it does not change the time itself
                dt = dt.replace(tzinfo=tz)
            else:
                # this converts a naive or tz-aware datetime to your timezone
                dt = dt.astimezone()
        # once the time has been set, convert to UTC
        if convert_to_utc:
            return dt.astimezone(tz=timezone.utc)
        elif localize_datetime:
            dt = dt.astimezone().replace(tzinfo=None)
    return dt


def parse_datetime(
    date_input: str | int | float,
    /,
    *,
    tz: timezone | zoneinfo.ZoneInfo | None = None,
    convert_to_utc: bool = False,
    localize_datetime: bool = False,
    parse_epoch_milliseconds: bool = False,
) -> datetime | None:
    """
    Tries to parse a datetime in lots of ways into a datetime object

    This does not assume anything about how the end timezone will be displayed,
    that is controlled by the flags
    """
    dt = _parse_datetime(date_input, parse_epoch_milliseconds=parse_epoch_milliseconds)
    if dt is None:
        return None
    return _handle_timezone(
        dt, tz=tz, convert_to_utc=convert_to_utc, localize_datetime=localize_datetime
    )


TIMEDELTA_REGEX = re.compile(
    r"^((?P<weeks>[\.\d]+?)w)?((?P<days>[\.\d]+?)d)?((?P<hours>[\.\d]+?)h)?((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$"
)


# https://stackoverflow.com/a/51916936
def parse_timedelta_string(timedelta_str: str) -> timedelta:
    """
    This uses a syntax similar to the 'GNU sleep' command
    e.g.: 1w5d5h10m50s means '1 week, 5 days, 5 hours, 10 minutes, 50 seconds'
    """
    parts = TIMEDELTA_REGEX.match(timedelta_str)
    if parts is None:
        raise ValueError(
            f"Could not parse time duration from {timedelta_str}.\nValid examples: '8h', '1w2d8h5m20s', '2m4s'"
        )
    time_params = {
        name: float(param) for name, param in parts.groupdict().items() if param
    }
    return timedelta(**time_params)


FMT_ALIASES = {
    "date": "%Y-%m-%d",
    "date_": "%Y_%m_%d",
    "time": "%H:%M:%S",
    "epoch": "%s",
    "day": "%d",
    "month": "%m",
    "year": "%Y",
    "week_of_year": "%U",
    "day_of_year": "%j",
    "usdate": "%m/%d/%Y",
}


def format_datetime(dt: datetime, /, *, format: str | None) -> str:
    if format is None:
        return dt.isoformat()
    if format in FMT_ALIASES:
        return dt.strftime(FMT_ALIASES[format])
    elif format == "human":
        try:
            import arrow
        except ImportError as ie:
            raise ImportError(
                f"'arrow' not installed, install with '{sys.executable} -m pip install arrow'"
            ) from ie

        return arrow.get(dt).humanize()
    elif format == "epoch_milliseconds":
        return str(int(dt.timestamp() * 1000))
    else:
        return dt.strftime(format)
