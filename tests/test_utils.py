from unittest.mock import patch

from mgallery.utils import binary_array_to_hex, get_gallery_file_list


class TestBinaryArrayToHex:
    def test_binary_array_to_hex_returns_string(self):
        binary_array = [1] * 64
        result = binary_array_to_hex(binary_array, hash_size=8)
        assert isinstance(result, str)

    def test_binary_array_to_hex_all_ones(self):
        binary_array = [1] * 64
        result = binary_array_to_hex(binary_array, hash_size=8)
        assert result == "ffffffffffffffff"

class TestGetGalleryFileList:
    @patch("mgallery.utils.glob")
    def test_get_gallery_file_list_empty(self, mock_glob):
        mock_glob.glob.return_value = []
        result = get_gallery_file_list(recursive=True)
        assert result == []
