# dateq

Meant to replace and collect all my dozens of tiny date scripts that do custom, little things

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

  Pass dates as arguments, or - to parse from STDIN

Options:
  --force-tz TZ                   timezone to use for naive dates (parsed dates without a timezone)
  --utc                           convert to UTC
  -L, --localize                  localize time to your current timezone
  -F, --format
      [date | date_ | day |
      day_of_year | epoch | epoch_milliseconds |
      human | month | python_strftime_string |
      time | usdate | week_of_year |
      weekday | weekday_name | year]
                                  format for date string
  --strict / --no-strict          raise an error if the date string could not be parsed  [default: strict]
  --dateparser-settings JSON      a json settings object to be used by the dateparser library
  -h, --help                      Show this message and exit.
```

### Examples

```bash
$ dateq parse now
2025-03-20T01:31:11.093906
$ dateq parse -Fepoch '3 hours ago'
1742448701
$ dateq parse -Ftime 'in 3 hours'
04:32:02
$ dateq parse -F'%H:%M' 'in 3 hours'
04:32
$ dateq parse -Fhuman '2025-03-20T01:31:11'
a minute ago
$ echo '1742459605' | dateq parse -
2025-03-20T01:33:25
$ dateq parse 'saturday at 3pm'
2025-03-15T15:00:00
$ dateq parse --dateparser-settings '{"PREFER_DATES_FROM": "future"}' 'saturday at 3pm'
2025-03-22T15:00:00
```

### Tests

```bash
git clone 'https://github.com/purarue/dateq'
cd ./dateq
pip install '.[testing]'
flake8 ./dateq
mypy ./dateq
```
