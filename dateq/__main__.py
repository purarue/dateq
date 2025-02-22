import os
import sys
import zoneinfo
from typing import Iterator, Iterable, Sequence

import click

from .click_helpers import _parse_timezone

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

    aliases.append("python_strftime_string")

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
            yield from click.get_text_stream("stdin")
        else:
            yield d


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
    help="force timezone for parsed dates",
    callback=_parse_timezone,
)
@click.option("--utc", is_flag=True, default=False, help="convert to UTC")
@click.option(
    "-l",
    "--localize",
    is_flag=True,
    default=False,
    help="localize time to your current timezone",
)
@click.option(
    "--format",
    metavar="FORMAT" if not LIST_FORMATS else _wrapped_fmt_list(),
    default=None,
    help="format for date string",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="raise an error if the date string is invalid",
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
) -> None:
    from .parser import parse_datetime, format_datetime

    for raw in _iter_inputs(date):
        dt = parse_datetime(
            raw, tz=force_tz, convert_to_utc=utc, localize_datetime=localize
        )
        if dt is None:
            if strict:
                click.echo(f"Invalid date: {raw}", err=True)
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
