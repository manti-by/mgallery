import pytest
from datetime import datetime
from unittest import TestCase

from core.utils import (
    extract_gallery_data,
    extract_image_data
)


class UtilsTestCase(TestCase):

    @pytest.mark.parametrize('path,expected', [
        ('/2009-2011 Ранние', {
            'year': '2009',
            'date': None,
            'name': 'Ранние',
        }),
        ('/2009-2011 Ранние/2009-11-17', {
            'year': '2009',
            'date': datetime.strptime('2009-11-17', '%Y-%m-%d').date(),
            'name': 'Ранние',
        }),
        ('/2009-2011 Ранние/2009-11-17', {
            'year': '2017',
            'date': datetime.strptime('2017-03-05', '%Y-%m-%d').date(),
            'name': 'Мерс',
        }),
        ('/2009-2011 Ранние/2009-05-01 Test', {
            'year': '2009',
            'date': datetime.strptime('2009-05-01', '%Y-%m-%d').date(),
            'name': 'Test',
        }),
    ])
    def test_extract_gallery_data(self, path, expected):
        data = extract_gallery_data(path)
        self.assertEqual(data, expected)

    @pytest.mark.parametrize('path,expected', [
        ('/2009-2011 Ранние/2009-05-01 Test/DSC00144.jpeg', {
            'camera': None,
            'lens': None,
            'position': None,
            'datetime': None,
            'phash': '9f916066a759496d',
        }),
        ('/2017 Весна/2017-03-05 Мерс/P70305-164500.jpg', {
            'camera': 'Meizu PRO 6',
            'lens': None,
            'position': '53.96010969444445, 27.538057305555558',
            'datetime': datetime.strptime('2017-03-05 16:45:02', '%Y-%m-%d %H:%M:%S'),
            'phash': 'edc1d22d05d03e8f',
        }),
        ('/2018 Весна/2018-05-05 Барселона/2018-05-08_12-14-46-56.jpg', {
            'camera': 'SONY SLT-A77V',
            'lens': 'DT 16-50mm F2.8 SSM',
            'position': '41.591363333333334, 1.8356766666666666',
            'datetime': datetime.strptime('2018-05-08 12:14:46', '%Y-%m-%d %H:%M:%S'),
            'phash': 'cc87cdc4d678b922',
        }),
    ])
    def test_extract_image_data(self, path, expected):
        data = extract_image_data(path)
        self.assertEqual(data, expected)
