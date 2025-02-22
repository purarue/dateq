import click
from datetime import datetime

import zoneinfo


def _parse_datetime(
    ctx: click.Context, param: click.Argument, value: str | None
) -> datetime | None:
    if value is None or value.strip() == "":
        return None

    from .parser import parse_datetime

    val = parse_datetime(value)
    if val is None:
        raise click.BadParameter(f"Invalid datetime: {value}")
    else:
        return val


def _parse_timezone(
    ctx: click.Context, param: click.Argument, value: str | None
) -> zoneinfo.ZoneInfo | None:
    if value is None:
        return None

    try:
        return zoneinfo.ZoneInfo(value)
    except zoneinfo.ZoneInfoNotFoundError:
        pass

    try:
        return zoneinfo.ZoneInfo(f"US/{value}")
    except zoneinfo.ZoneInfoNotFoundError:
        pass

    raise click.BadParameter(f"Invalid timezone: {value}")
