# dateq

WIP; this is meant to replace and collect all my dozens of tiny date scripts that do custom, little things

A command line date/time processor (pronounced, like [`jq`](https://jqlang.org/); `date`-`q`)

## Installation

Requires `python3.10+`

To install with pip, run:

```
pip install git+https://github.com/purarue/dateq
```

## Usage

```
Usage: dateq parse [OPTIONS] DATE...

Options:
  --force-tz TZ    force timezone for parsed dates
  --utc            convert to UTC
  -l, --localize   localize time to your current timezone
  --format FORMAT  format for date string
  --strict         raise an error if the date string is invalid
  -h, --help       Show this message and exit.

  For a list of all formats, run 'LIST_FORMATS=1 dateq parse --help'
```

### Tests

```bash
git clone 'https://github.com/purarue/dateq'
cd ./dateq
pip install '.[testing]'
pytest
flake8 ./dateq
mypy ./dateq
```
