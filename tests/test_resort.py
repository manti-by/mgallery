from unittest.mock import MagicMock, patch

import pytest

from mgallery.services.resort import get_path_from_filename, month_to_season


class TestMonthToSeason:
    @pytest.mark.parametrize("month,expected", [(1, "Зима"), (2, "Зима"), (12, "Зима"), (3, "Весна"), (4, "Весна"), (5, "Весна"), (6, "Лето"), (7, "Лето"), (8, "Лето"), (9, "Осень"), (10, "Осень"), (11, "Осень")])
    def test_month_to_season(self, month, expected):
        result = month_to_season(month)
        assert result == expected


class TestGetPathFromFilename:
    def test_get_path_from_filename_winter(self):
        result = get_path_from_filename("2024-01-15_10-30-00.jpg")
        gallery, date, _ = result
        assert gallery == "2024 Зима"
        assert date == "2024-01-15"


class TestRunResort:
    @patch("mgallery.services.resort.get_gallery_file_list")
    @patch("mgallery.services.resort.Path")
    def test_run_resort(self, mock_path_cls, mock_get_files):
        mock_get_files.return_value = []
        mock_path_cls.return_value.mkdir = MagicMock()
        from mgallery.services.resort import run_resort
        run_resort()
        mock_get_files.assert_called_once()