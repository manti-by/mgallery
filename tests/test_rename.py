from unittest.mock import MagicMock, patch

from mgallery.services.rename import get_datetime_from_exif, get_datetime_from_filename


class TestGetDatetimeFromExif:
    @patch("mgallery.services.rename.open", create=True)
    @patch("mgallery.services.rename.exifread")
    def test_get_datetime_from_exif_success(self, mock_exif, mock_file):
        mock_exif.process_file.return_value = {"EXIF DateTimeOriginal": "2024:01:15 10:30:00"}
        mock_file.return_value.__enter__.return_value.read = MagicMock()
        result = get_datetime_from_exif("/path/to/image.jpg")
        assert result is not None
        assert result.year == 2024

    @patch("mgallery.services.rename.open", create=True)
    @patch("mgallery.services.rename.exifread")
    def test_get_datetime_from_exif_no_exif(self, mock_exif, mock_file):
        mock_exif.process_file.return_value = {}
        mock_file.return_value.__enter__.return_value.read = MagicMock()
        result = get_datetime_from_exif("/path/to/image.jpg")
        assert result is None


class TestGetDatetimeFromFilename:
    def test_get_datetime_from_filename_img_format(self):
        result = get_datetime_from_filename("IMG_20140803_075125.jpg")
        assert result is not None
        assert result.year == 2014

    def test_get_datetime_from_filename_no_match(self):
        result = get_datetime_from_filename("random_file_name.jpg")
        assert result is None