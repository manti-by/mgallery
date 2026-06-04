from sqlalchemy import create_engine

from mgallery.library.tables import Base


def create_test_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine