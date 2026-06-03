import pytest
from sqlalchemy import create_engine, text

from mgallery.library.tables import Base


@pytest.fixture
def mock_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    connection = engine.connect()
    connection.begin()
    return connection


@pytest.fixture
def db_with_data(mock_db_session):
    mock_db_session.execute(
        text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
        {"path": "test", "name": "img1.jpg", "phash": "abc123", "width": 100, "height": 100, "size": 1000},
    )
    mock_db_session.execute(
        text("INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"),
        {"path": "test", "name": "img2.jpg", "phash": "abc123", "width": 200, "height": 200, "size": 2000},
    )
    mock_db_session.commit()
    return mock_db_session