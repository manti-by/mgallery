from collections import defaultdict
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from mgallery.utils.settings import DATABASE_URL


class Database:
    def __init__(self, engine: Engine | None = None):
        self._engine = engine or create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,
        )
        self._session_factory = sessionmaker(bind=self._engine)

    def _session(self) -> Session:
        return self._session_factory()

    def get(self, key: str | bytes) -> dict[str, Any]:
        key_str = key.decode() if isinstance(key, bytes) else key
        parts = key_str.split("-", 1)
        if len(parts) != 2:
            return {}
        phash, rest = parts
        if "/" not in rest:
            return {}
        path, name = rest.rsplit("/", 1)
        if phash == "None":
            with self._session() as session:
                row = session.execute(
                    text("SELECT path, name, phash, width, height, size FROM images WHERE phash IS NULL AND path = :path AND name = :name"),
                    {"path": path, "name": name},
                ).mappings().first()
                if row:
                    return dict(row)
        else:
            with self._session() as session:
                row = session.execute(
                    text("SELECT path, name, phash, width, height, size FROM images WHERE phash = :phash AND path = :path AND name = :name"),
                    {"phash": phash, "path": path, "name": name},
                ).mappings().first()
                if row:
                    return dict(row)
        return {}

    def all(self, pattern: str = "*") -> list[dict[str, Any]]:
        if pattern == "*":
            with self._session() as session:
                rows = session.execute(text("SELECT path, name, phash, width, height, size FROM images")).mappings().all()
        else:
            with self._session() as session:
                rows = session.execute(
                    text("SELECT path, name, phash, width, height, size FROM images WHERE path LIKE :pattern"),
                    {"pattern": f"%{pattern}%"},
                ).mappings().all()
        return [dict(row) for row in rows]

    def duplicates(self) -> dict[str, list[dict[str, Any]]]:
        with self._session() as session:
            rows = session.execute(
                text("""
                    SELECT path, name, phash, width, height, size
                    FROM images
                    WHERE phash IN (
                        SELECT phash FROM images WHERE phash IS NOT NULL
                        GROUP BY phash
                        HAVING COUNT(*) > 1
                    )
                """),
            ).mappings().all()
        result: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            item = dict(row)
            if item["phash"]:
                result[item["phash"]].append(item)
        return result

    def create(
        self,
        path: str,
        name: str,
        phash: str | None = None,
        width: int | None = None,
        height: int | None = None,
        size: int | None = None,
        session: Session | None = None,
    ):
        external_session = session is not None
        session = session or self._session()
        try:
            session.execute(
                text("""
                    INSERT INTO images (path, name, phash, width, height, size)
                    VALUES (:path, :name, :phash, :width, :height, :size)
                    ON CONFLICT (path, name) DO UPDATE SET
                        phash = COALESCE(EXCLUDED.phash, images.phash),
                        width = COALESCE(EXCLUDED.width, images.width),
                        height = COALESCE(EXCLUDED.height, images.height),
                        size = COALESCE(EXCLUDED.size, images.size)
                """),
                {"path": path, "name": name, "phash": phash, "width": width, "height": height, "size": size},
            )
            if not external_session:
                session.commit()
        finally:
            if not external_session:
                session.close()

    def create_batch(self, items: list[dict[str, Any]], session: Session | None = None) -> None:
        external_session = session is not None
        session = session or self._session()
        try:
            for item in items:
                session.execute(
                    text("""
                        INSERT INTO images (path, name, phash, width, height, size)
                        VALUES (:path, :name, :phash, :width, :height, :size)
                        ON CONFLICT (path, name) DO UPDATE SET
                            phash = COALESCE(EXCLUDED.phash, images.phash),
                            width = COALESCE(EXCLUDED.width, images.width),
                            height = COALESCE(EXCLUDED.height, images.height),
                            size = COALESCE(EXCLUDED.size, images.size)
                    """),
                    {
                        "path": item["path"],
                        "name": item["name"],
                        "phash": item.get("phash"),
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "size": item.get("size"),
                    },
                )
            if not external_session:
                session.commit()
        finally:
            if not external_session:
                session.close()

    def delete(self, path: str, name: str):
        with self._session() as session:
            session.execute(
                text("DELETE FROM images WHERE path = :path AND name = :name"),
                {"path": path, "name": name},
            )
            session.commit()