from unittest.mock import MagicMock, patch

from mgallery.thumbnails import create_thumbnails, get_duplicates_chunks


class TestGetDuplicatesChunks:
    @patch("mgallery.thumbnails.Database")
    def test_get_duplicates_chunks_empty(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.duplicates.return_value = {}
        mock_db_class.return_value = mock_db
        result = get_duplicates_chunks(num_cores=1)
        assert isinstance(result, list)

    @patch("mgallery.thumbnails.Database")
    def test_get_duplicates_chunks_with_duplicates(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.duplicates.return_value = {"abc": [{"name": "img1"}, {"name": "img2"}]}
        mock_db_class.return_value = mock_db
        result = get_duplicates_chunks(num_cores=1)
        assert isinstance(result, list)

class TestCreateThumbnails:
    @patch("mgallery.thumbnails.create_thumbnail")
    def test_create_thumbnails_skips_gif(self, mock_create_thumbnail):
        duplicates = {"abc": [{"path": "test", "name": "image.gif"}, {"path": "test", "name": "image.jpg"}]}
        create_thumbnails(duplicates, 0)
        assert mock_create_thumbnail.call_count == 1

    @patch("mgallery.thumbnails.create_thumbnail")
    def test_create_thumbnails_calls_create(self, mock_create_thumbnail):
        duplicates = {"abc": [{"path": "test", "name": "image1.jpg"}, {"path": "test", "name": "image2.jpg"}]}
        create_thumbnails(duplicates, 0)
        assert mock_create_thumbnail.call_count == 2
