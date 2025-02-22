import pytest
from datetime import datetime
from dateq.parser import parse_datetime


def test_parsing() -> None:
    assert parse_datetime("2020-01-01") == datetime(2020, 1, 1)
    assert parse_datetime(1740204794) == datetime(2025, 2, 21, 22, 13, 14)


if __name__ == "__main__":
    pytest.main()
