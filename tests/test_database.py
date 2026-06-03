from unittest.mock import patch

from sqlalchemy import create_engine, text

from mgallery.library.database import Database
from mgallery.library.tables import Base


class TestDatabase:
    def test_database_init(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            assert db.engine is not None

    def test_create(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            db.create(path="test", name="image.jpg", phash="abc123", width=100, height=100, size=1000)
            result = list(engine.connect().execute(text("SELECT * FROM images")))
            assert len(result) == 1
            assert result[0].path == "test"
            assert result[0].name == "image.jpg"
            assert result[0].phash == "abc123"

    def test_get_returns_dict(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        conn = engine.connect()
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "img1.jpg", "phash": "abc", "width": 100, "height": 100, "size": 1000},
        )
        conn.commit()
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            result = db.get("abc-test/img1.jpg")
            assert result["path"] == "test"
            assert result["name"] == "img1.jpg"
            assert result["phash"] == "abc"

    def test_get_returns_empty_dict_when_not_found(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            result = db.get("nonexistent-key")
            assert result == {}

    def test_all_returns_list(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        conn = engine.connect()
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "img1.jpg", "phash": "abc", "width": 100, "height": 100, "size": 1000},
        )
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "img2.jpg", "phash": "def", "width": 200, "height": 200, "size": 2000},
        )
        conn.commit()
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            result = db.all()
            assert len(result) == 2

    def test_delete(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        conn = engine.connect()
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "image.jpg", "phash": "abc", "width": 100, "height": 100, "size": 1000},
        )
        conn.commit()
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            db.delete("test", "image.jpg")
            result = list(engine.connect().execute(text("SELECT * FROM images")))
            assert len(result) == 0

    def test_duplicates_returns_dict(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        conn = engine.connect()
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "img1.jpg", "phash": "abc", "width": 100, "height": 100, "size": 1000},
        )
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "img2.jpg", "phash": "abc", "width": 200, "height": 200, "size": 900},
        )
        conn.commit()
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            result = db.duplicates()
            assert "abc" in result
            assert len(result["abc"]) == 2

    def test_duplicates_filters_single_images(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        conn = engine.connect()
        conn.execute(
            text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
            {"path": "test", "name": "img1.jpg", "phash": "abc", "width": 100, "height": 100, "size": 1000},
        )
        conn.commit()
        with patch("mgallery.library.database.create_engine", return_value=engine):
            db = Database()
            result = db.duplicates()
            assert result == {}