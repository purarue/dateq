"""Regression tests for out-of-range epoch timestamp handling."""

from click.testing import CliRunner

from dateq.__main__ import main
from dateq.parser import parse_datetime


def test_huge_epoch_returns_none() -> None:
    # used to raise OverflowError (or OSError on some platforms)
    assert parse_datetime("99999999999999999999") is None


def test_negative_huge_epoch_returns_none() -> None:
    assert parse_datetime("-99999999999999999999") is None


def test_huge_epoch_cli_clean_error() -> None:
    result = CliRunner().invoke(main, ["parse", "99999999999999999999"])
    assert result.exit_code == 1
    assert "error parsing" in result.output
    assert "Traceback" not in result.output


def test_normal_epoch_still_parses() -> None:
    assert parse_datetime("0") is not None
