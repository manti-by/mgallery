from unittest.mock import MagicMock, patch

from mgallery.dump import run_dump


class TestRunDump:
    @patch("mgallery.dump.Database")
    @patch("mgallery.dump.open", create=True)
    def test_run_dump(self, mock_open, mock_db_class):
        mock_db = MagicMock()
        mock_db.all.return_value = [{"name": "img1"}, {"name": "img2"}]
        mock_db_class.return_value = mock_db
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        run_dump()
        mock_file.write.assert_called_once()
        mock_db.all.assert_called_once()
