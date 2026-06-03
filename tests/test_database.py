import json
from unittest.mock import patch

from mgallery.database import Database


class TestDatabase:
    def test_database_init(self, mock_redis_client):
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            Database()
            mock_redis.from_url.assert_called_once()

    def test_get_returns_dict(self, mock_redis_client):
        mock_redis_client.get.return_value = json.dumps({"key": "value"}).encode()
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            result = db.get("test_key")
            assert result == {"key": "value"}

    def test_get_returns_empty_dict_when_not_found(self, mock_redis_client):
        mock_redis_client.get.return_value = None
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            result = db.get("nonexistent_key")
            assert result == {}

    def test_all_returns_list(self, mock_redis_client):
        mock_redis_client.keys.return_value = [b"key1", b"key2"]
        mock_redis_client.get.side_effect = [json.dumps({"name": "img1"}).encode(), json.dumps({"name": "img2"}).encode()]
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            result = db.all()
            assert len(result) == 2

    def test_create(self, mock_redis_client):
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            db.create(path="test", name="image.jpg", phash="abc123", width=100, height=100, size=1000)
            mock_redis_client.set.assert_called_once()

    def test_delete(self, mock_redis_client):
        mock_redis_client.keys.return_value = [b"key1"]
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            db.delete("test", "image.jpg")
            mock_redis_client.keys.assert_called()
            mock_redis_client.delete.assert_called_once()

    def test_duplicates_returns_dict(self, mock_redis_client):
        mock_redis_client.keys.return_value = [b"abc-test/img1", b"abc-test/img2"]
        mock_redis_client.get.side_effect = [json.dumps({"path": "test", "name": "img1", "phash": "abc", "size": 1000}).encode(), json.dumps({"path": "test", "name": "img2", "phash": "abc", "size": 900}).encode()]
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            result = db.duplicates()
            assert "abc" in result

    def test_duplicates_filters_single_images(self, mock_redis_client):
        mock_redis_client.keys.return_value = [b"abc-test/img1"]
        mock_redis_client.get.return_value = json.dumps({"path": "test", "name": "img1", "phash": "abc"}).encode()
        with patch("mgallery.database.redis") as mock_redis:
            mock_redis.from_url.return_value = mock_redis_client
            db = Database()
            result = db.duplicates()
            assert result == {}
