from unittest.mock import patch

from mgallery.scanner import get_file_chunks


class TestGetFileChunks:
    @patch("mgallery.scanner.get_gallery_file_list")
    def test_get_file_chunks_empty(self, mock_get_files):
        mock_get_files.return_value = []
        result = get_file_chunks(num_cores=2)
        assert isinstance(result, list)

    @patch("mgallery.scanner.get_gallery_file_list")
    def test_get_file_chunks_single_file(self, mock_get_files):
        mock_get_files.return_value = ["/path/to/image.jpg"]
        result = get_file_chunks(num_cores=1)
        assert len(result) == 1

    @patch("mgallery.scanner.get_gallery_file_list")
    def test_get_file_chunks_multiple_files(self, mock_get_files):
        mock_get_files.return_value = [f"/path/to/image{i}.jpg" for i in range(10)]
        result = get_file_chunks(num_cores=2)
        total_files = sum(len(chunk) for chunk in result)
        assert total_files == 10
