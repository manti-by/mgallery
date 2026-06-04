import pytest

from tests.conftest import create_test_engine

from mgallery.library.database import Database


@pytest.fixture
def test_engine():
    return create_test_engine()


@pytest.fixture
def database(test_engine):
    return Database(engine=test_engine)


class TestDatabase:
    def test_database_init(self, test_engine):
        db = Database(engine=test_engine)
        assert db._engine is test_engine

    def test_get_returns_dict(self, database):
        database.create(path="test", name="image.jpg", phash="abc123", width=100, height=100, size=1000)
        result = database.get("abc123-test/image.jpg")
        assert result["path"] == "test"
        assert result["name"] == "image.jpg"
        assert result["phash"] == "abc123"

    def test_get_returns_empty_dict_when_not_found(self, database):
        result = database.get("nonexistent-key")
        assert result == {}

    def test_all_returns_list(self, database):
        database.create(path="test", name="img1.jpg", phash="abc", width=100, height=100, size=1000)
        database.create(path="test", name="img2.jpg", phash="abc", width=100, height=100, size=900)
        result = database.all()
        assert len(result) == 2

    def test_create(self, database):
        database.create(path="test", name="image.jpg", phash="abc123", width=100, height=100, size=1000)
        result = database.all()
        assert len(result) == 1
        assert result[0]["name"] == "image.jpg"

    def test_delete(self, database):
        database.create(path="test", name="image.jpg", phash="abc", width=100, height=100, size=1000)
        database.delete("test", "image.jpg")
        result = database.all()
        assert len(result) == 0

    def test_duplicates_returns_dict(self, database):
        database.create(path="test", name="img1.jpg", phash="abc", width=100, height=100, size=1000)
        database.create(path="test", name="img2.jpg", phash="abc", width=100, height=100, size=900)
        result = database.duplicates()
        assert "abc" in result
        assert len(result["abc"]) == 2

    def test_duplicates_filters_single_images(self, database):
        database.create(path="test", name="img1.jpg", phash="abc", width=100, height=100, size=1000)
        result = database.duplicates()
        assert result == {}

    def test_all_with_pattern(self, database):
        database.create(path="folder1", name="img1.jpg", phash="abc", width=100, height=100, size=1000)
        database.create(path="folder2", name="img2.jpg", phash="def", width=100, height=100, size=900)
        result = database.all("folder1")
        assert len(result) == 1
        assert result[0]["path"] == "folder1"