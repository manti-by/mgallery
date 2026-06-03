from unittest.mock import MagicMock, patch

from mgallery.autodelete import run_autodelete


class TestRunAutodelete:
    @patch("mgallery.autodelete.Database")
    @patch("mgallery.autodelete.os")
    def test_run_autodelete_deletes_duplicates(self, mock_os, mock_db_class):
        mock_db = MagicMock()
        mock_db.duplicates.return_value = {"abc123": [{"path": "test", "name": "img1.jpg", "size": 1000}, {"path": "test", "name": "img2.jpg", "size": 500}]}
        mock_db_class.return_value = mock_db
        mock_os.path.exists.return_value = True
        run_autodelete()
        assert mock_db.delete.call_count == 1

    @patch("mgallery.autodelete.Database")
    @patch("mgallery.autodelete.os")
    def test_run_autodelete_removes_thumbnail(self, mock_os, mock_db_class):
        mock_db = MagicMock()
        mock_db.duplicates.return_value = {"abc123": [{"path": "test", "name": "img1.jpg", "size": 1000}, {"path": "test", "name": "img2.jpg", "size": 500}]}
        mock_db_class.return_value = mock_db
        mock_os.path.exists.side_effect = [True, True]
        mock_os.remove = MagicMock()
        run_autodelete()
        assert mock_os.remove.call_count == 2
