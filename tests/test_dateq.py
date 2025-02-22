import pytest
from datetime import datetime, timezone
from dateq.parser import parse_datetime


def test_parsing() -> None:
    assert parse_datetime("2020-01-01") == datetime(2020, 1, 1)
    assert parse_datetime(1740204794, tz=timezone.utc, convert_to_utc=True) == datetime(
        2025, 2, 21, 22, 13, 14, tzinfo=timezone.utc
    )


if __name__ == "__main__":
    pytest.main()
