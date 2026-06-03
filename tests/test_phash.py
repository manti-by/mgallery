from unittest.mock import patch

import numpy as np

from mgallery.library.phash import get_image_phash


class TestGetImagePhash:
    @patch("mgallery.library.phash.cv2")
    @patch("mgallery.library.phash.numpy")
    def test_get_image_phash_success(self, mock_numpy, mock_cv2):
        mock_image = np.ones((24, 24, 3), dtype=np.uint8)
        mock_numpy.asarray.return_value = mock_image
        mock_numpy.float32.return_value = mock_image
        mock_numpy.median.return_value = 100
        dct_mock = np.zeros((6, 6))
        dct_mock[0, 0] = 200
        mock_cv2.dct.return_value = dct_mock
        result = get_image_phash(mock_image)
        assert result is not None
        assert isinstance(result, str)

    @patch("mgallery.library.phash.cv2")
    @patch("mgallery.library.phash.numpy")
    def test_get_image_phash_with_none_image(self, mock_numpy, mock_cv2):
        mock_numpy.asarray.side_effect = ValueError("image is None")
        mock_image = np.array([])
        result = get_image_phash(mock_image)
        assert result is None

    @patch("mgallery.library.phash.cv2")
    @patch("mgallery.library.phash.numpy")
    def test_get_image_phash_with_wrong_size(self, mock_numpy, mock_cv2):
        mock_image = np.ones((10, 10, 3), dtype=np.uint8)
        mock_numpy.asarray.return_value = mock_image
        mock_numpy.float32.return_value = mock_image
        mock_cv2.resize.return_value = np.ones((24, 24), dtype=np.uint8)
        dct_mock = np.zeros((6, 6))
        mock_cv2.dct.return_value = dct_mock
        mock_numpy.median.return_value = 100
        result = get_image_phash(mock_image)
        assert result is not None