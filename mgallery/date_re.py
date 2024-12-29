import re
from datetime import datetime
from typing import AnyStr


def date_compiler_01(matches: re.Match[AnyStr] | None) -> datetime:
    month = datetime.strptime(matches.group("month"), "%B").month
    hours_minutes = datetime.strptime(
        f"{matches.group('hours')}{matches.group('minutes')}{matches.group('ampm')}",
        "%I%M%p",
    )
    return datetime(
        int(matches.group("year")),
        month,
        int(matches.group("day")),
        hours_minutes.hour,
        hours_minutes.minute,
        int(matches.group("day")),
    )


def date_compiler_02(matches: re.Match[AnyStr] | None) -> datetime:
    return datetime(
        int(matches.group("year")),
        int(matches.group("month")),
        int(matches.group("day")),
        int(matches.group("hours")),
        int(matches.group("minutes")),
        int(matches.group("seconds")),
    )


def date_compiler_03(matches: re.Match[AnyStr] | None) -> datetime:
    year = 2010 + int(matches.group("year"))
    return datetime(
        year,
        int(matches.group("month")),
        int(matches.group("day")),
        int(matches.group("hours")),
        int(matches.group("minutes")),
        int(matches.group("seconds")),
    )


def date_compiler_04(matches: re.Match[AnyStr] | None) -> datetime:
    return datetime(
        int(matches.group("year")),
        int(matches.group("month")),
        int(matches.group("day")),
        int(matches.group("hours")),
        int(matches.group("minutes")),
        int(matches.group("seconds")),
    )


DATE_PARSERS = {
    # January_30__2017_at_0733PM
    re.compile(
        r"(?P<month>\w*)_(?P<day>\d{2})__(?P<year>\d{4})_at_(?P<hours>\d{2})(?P<minutes>\d{2})(?P<ampm>\w{2}).*"
    ): date_compiler_01,
    # 20171222_232414
    re.compile(
        r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2}).*"
    ): date_compiler_02,
    # P61126-233638
    re.compile(
        r"P(?P<year>\d)(?P<month>\d{2})(?P<day>\d{2})-(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2}).*"
    ): date_compiler_03,
    # IMG_20140803_075125
    re.compile(
        r"(IMG|VID|PANO)_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2}).*"  # noqa
    ): date_compiler_04,
}
