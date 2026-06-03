from unittest.mock import MagicMock, patch

from mgallery.library import image

from mgallery.utils import settings


class TestProcessRawImage:
    @patch("mgallery.library.image.get_image_phash")
    @patch("mgallery.library.image.rawpy")
    @patch("mgallery.library.image.Database")
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
    @patch("mgallery.library.image.os.path.exists")
    @patch("mgallery.library.image.os.makedirs")
    @patch("mgallery.library.image.Image")
    @patch("mgallery.library.image.rawpy")
    def test_create_thumbnail_no_force(self, mock_rawpy, mock_image_cls, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        result = image.create_thumbnail("test", "image.jpg", size=128, force=False)
        assert result.startswith(settings.THUMBNAILS_PATH)

    @patch("mgallery.library.image.os.path.exists")
    @patch("mgallery.library.image.os.makedirs")
    @patch("mgallery.library.image.Image")
    @patch("mgallery.library.image.rawpy")
    def test_create_thumbnail_force(self, mock_rawpy, mock_image_cls, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        mock_image = MagicMock()
        mock_image_cls.open.return_value = mock_image
        mock_image_cls.fromarray.return_value = mock_image
        image.create_thumbnail("test", "image.jpg", size=128, force=True)
        mock_image.save.assert_called_once()


class TestProcessImage:
    @patch("mgallery.library.image.os.path.getsize")
    @patch("mgallery.library.image.process_rgb_image")
    def test_process_image_jpg(self, mock_process_rgb, mock_getsize):
        mock_getsize.return_value = 1024
        mock_db = MagicMock()
        image.process_image(mock_db, "test", "image.jpg")
        mock_process_rgb.assert_called_once()

    @patch("mgallery.library.image.os.path.getsize")
    @patch("mgallery.library.image.process_raw_image")
    def test_process_image_arw(self, mock_process_raw, mock_getsize):
        mock_getsize.return_value = 1024
        mock_db = MagicMock()
        image.process_image(mock_db, "test", "image.arw")
        mock_process_raw.assert_called_once()

    @patch("mgallery.library.image.os.path.getsize")
    @patch("mgallery.library.image.process_raw_image")
    def test_process_image_dng(self, mock_process_raw, mock_getsize):
        mock_getsize.return_value = 1024
        mock_db = MagicMock()
        image.process_image(mock_db, "test", "image.dng")
        mock_process_raw.assert_called_once()