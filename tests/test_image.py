from unittest.mock import MagicMock, patch

from mgallery import image, settings


class TestProcessRawImage:
    @patch("mgallery.image.get_image_phash")
    @patch("mgallery.image.rawpy")
    @patch("mgallery.image.Database")
    def test_process_raw_image_success(self, mock_db_class, mock_rawpy, mock_phash):
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_raw = MagicMock()
        mock_raw.postprocess.return_value = MagicMock(shape=[1080, 1920, 3])
        mock_rawpy.imread.return_value.__enter__.return_value = mock_raw
        mock_phash.return_value = "abc123"
        image.process_raw_image(mock_db, "test", "image.arw", 1024000)
        mock_db.create.assert_called_once()

class TestCreateThumbnail:
    @patch("mgallery.image.os.path.exists")
    @patch("mgallery.image.os.makedirs")
    @patch("mgallery.image.Image")
    @patch("mgallery.image.rawpy")
    def test_create_thumbnail_no_force(self, mock_rawpy, mock_image_cls, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        result = image.create_thumbnail("test", "image.jpg", size=128, force=False)
        assert result.startswith(settings.THUMBNAILS_PATH)

    @patch("mgallery.image.os.path.exists")
    @patch("mgallery.image.os.makedirs")
    @patch("mgallery.image.Image")
    @patch("mgallery.image.rawpy")
    def test_create_thumbnail_force(self, mock_rawpy, mock_image_cls, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        mock_image = MagicMock()
        mock_image_cls.open.return_value = mock_image
        mock_image_cls.fromarray.return_value = mock_image
        image.create_thumbnail("test", "image.jpg", size=128, force=True)
        mock_image.save.assert_called_once()

class TestProcessImage:
    @patch("mgallery.image.os.path.getsize")
    @patch("mgallery.image.process_rgb_image")
    def test_process_image_jpg(self, mock_process_rgb, mock_getsize):
        mock_getsize.return_value = 1024
        mock_db = MagicMock()
        image.process_image(mock_db, "test", "image.jpg")
        mock_process_rgb.assert_called_once()

    @patch("mgallery.image.os.path.getsize")
    @patch("mgallery.image.process_raw_image")
    def test_process_image_arw(self, mock_process_raw, mock_getsize):
        mock_getsize.return_value = 1024
        mock_db = MagicMock()
        image.process_image(mock_db, "test", "image.arw")
        mock_process_raw.assert_called_once()

    @patch("mgallery.image.os.path.getsize")
    @patch("mgallery.image.process_raw_image")
    def test_process_image_dng(self, mock_process_raw, mock_getsize):
        mock_getsize.return_value = 1024
        mock_db = MagicMock()
        image.process_image(mock_db, "test", "image.dng")
        mock_process_raw.assert_called_once()
