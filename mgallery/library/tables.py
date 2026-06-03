from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(512), nullable=False)
    name = Column(String(256), nullable=False)
    phash = Column(String(32), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    size = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")