import re

from mgallery.date_re import DATE_PARSERS, date_compiler_01, date_compiler_02, date_compiler_03, date_compiler_04


class TestDateCompiler01:
    def test_january_30_2017_at_0733pm(self):
        pattern = re.compile(r"(?P<month>\w*)_(?P<day>\d{2})__(?P<year>\d{4})_at_(?P<hours>\d{2})(?P<minutes>\d{2})(?P<ampm>\w{2}).*")
        match = pattern.search("January_30__2017_at_0733PM.jpg")
        assert match is not None
        result = date_compiler_01(match)
        assert result.year == 2017
        assert result.month == 1

class TestDateCompiler02:
    def test_20171222_232414(self):
        pattern = re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2}).*")
        match = pattern.search("20171222_232414.jpg")
        assert match is not None
        result = date_compiler_02(match)
        assert result.year == 2017

class TestDateCompiler03:
    def test_p61126_233638(self):
        pattern = re.compile(r"P(?P<year>\d)(?P<month>\d{2})(?P<day>\d{2})-(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2}).*")
        match = pattern.search("P61126-233638.jpg")
        assert match is not None
        result = date_compiler_03(match)
        assert result.year == 2016

class TestDateCompiler04:
    def test_img_20140803_075125(self):
        pattern = re.compile(r"(IMG|VID|PANO)_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2}).*")
        match = pattern.search("IMG_20140803_075125.jpg")
        assert match is not None
        result = date_compiler_04(match)
        assert result.year == 2014

class TestDateParsers:
    def test_date_parsers_not_empty(self):
        assert len(DATE_PARSERS) == 4

    def test_all_patterns_are_compiled(self):
        for pattern in DATE_PARSERS.keys():
            assert isinstance(pattern, re.Pattern)
