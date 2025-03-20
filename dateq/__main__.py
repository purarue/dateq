import os
import sys
import zoneinfo
from typing import Iterator, Iterable, Sequence, Any, TYPE_CHECKING, Union

import click

from .click_helpers import _parse_timezone

if TYPE_CHECKING:
    from dateparser import _Settings

CONTEXT_SETTINGS = {
    "max_content_width": 110,
    "show_default": True,
    "help_option_names": ["-h", "--help"],
}


@click.group(context_settings=CONTEXT_SETTINGS)
def main() -> None:
    pass


LIST_FORMATS = "LIST_FORMATS" in os.environ


def _chunk_list(lst: Iterable[str], n: int) -> Iterator[list[str]]:
    lst = list(lst)
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _wrapped_fmt_list() -> str:
    import textwrap

    list_formats_per_line = int(os.environ.get("LIST_FORMAT_PER_LINE", 3))

    from .parser import FMT_ALIASES

    aliases = list(FMT_ALIASES.keys())

    aliases.extend(["human", "epoch_milliseconds", "python_strftime_string"])
    aliases.sort()

    # split into groups of 6, join each group with ' | '
    lines_fmted: list[str] = [
        " | ".join(chunk) for chunk in _chunk_list(aliases, list_formats_per_line)
    ]

    # add [ and ] to first and last
    lines_fmted[0] = "[" + lines_fmted[0]
    lines_fmted[-1] = lines_fmted[-1] + "]"

    # add | to the end of each line (separator between choices), except the last
    for i in range(0, len(lines_fmted) - 1):
        lines_fmted[i] = lines_fmted[i] + " |"

    return textwrap.indent("\n" + "\n".join(lines_fmted), " " * 6)


def _iter_inputs(date: Sequence[str]) -> Iterator[str]:
    for d in date:
        if d == "-":
            for line in click.get_text_stream("stdin"):
                yield line.rstrip(os.linesep)
        else:
            yield d


def _parse_settings(settings: str | None) -> dict[str, Any] | None:
    if settings is not None and settings.strip():
        import json

        try:
            item = json.loads(settings)
        except json.JSONDecodeError:
            raise click.BadParameter(f"Invalid JSON: '{settings}'")
        if not isinstance(item, dict):
            raise click.BadParameter(
                f"Settings should be a dict (a top-level JSON object), not {type(item).__name__}"
            )
        return item
    return None


@main.command(
    short_help="parse dates",
    epilog=(
        "For a list of all formats, run 'LIST_FORMATS=1 dateq parse --help'"
        if not LIST_FORMATS
        else None
    ),
)
@click.option(
    "--force-tz",
    default=None,
    metavar="TZ",
    help="timezone to use for naive dates (parsed dates without a timezone)",
    callback=_parse_timezone,
)
@click.option("--utc", is_flag=True, default=False, help="convert to UTC")
@click.option(
    "-L",
    "--localize",
    is_flag=True,
    default=False,
    help="localize time to your current timezone",
)
@click.option(
    "-F",
    "--format",
    metavar="FORMAT" if not LIST_FORMATS else _wrapped_fmt_list(),
    default=None,
    help="format for date string",
)
@click.option(
    "--strict/--no-strict",
    is_flag=True,
    default=True,
    help="raise an error if the date string could not be parsed",
)
@click.option(
    "--dateparser-settings",
    default=None,
    metavar="JSON",
    help="a json settings object to be used by the dateparser library",
    type=str,
    callback=lambda _, __, value: _parse_settings(value) if value else None,
)
@click.argument(
    "DATE",
    required=True,
    type=str,
    nargs=-1,
)
def parse(
    utc: bool,
    localize: bool,
    format: str,
    strict: bool,
    force_tz: zoneinfo.ZoneInfo | None,
    date: Sequence[str],
    dateparser_settings: Union["_Settings", None],
) -> None:
    """
    Pass dates as arguments, or - to parse from STDIN
    """
    from .parser import parse_datetime, format_datetime

    if format == "python_strftime_string":
        raise click.BadParameter(
            "Not literally 'python_strftime_string', you can pass any strftime format string, e.g. %H:%M, %Y-%m-%d, %Y-%m-%d %H:%M:%S; See https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes"
        )

    for raw in _iter_inputs(date):
        dt = parse_datetime(
            raw,
            tz=force_tz,
            convert_to_utc=utc,
            localize_datetime=localize,
            dateparser_settings=dateparser_settings,
        )
        if dt is None:
            if strict:
                click.echo(f"dateq: error parsing '{raw}'", err=True)
                sys.exit(1)
            else:
                click.echo(raw)
        else:
            click.echo(format_datetime(dt, format=format))


@main.command(short_help="list all timezones", name="list-tzs")
def list_timezones() -> None:
    import zoneinfo

    for tz in zoneinfo.available_timezones():
        click.echo(tz)


if __name__ == "__main__":
    main(prog_name="dateq")
