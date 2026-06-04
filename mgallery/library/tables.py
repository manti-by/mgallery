from sqlalchemy import BigInteger, Integer, MetaData, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData()


class Image(Base):
    __tablename__ = "images"
    __table_args__ = (UniqueConstraint("path", "name", name="uq_images_path_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    phash: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)