from collections import defaultdict

from sqlalchemy import create_engine, text

from mgallery.utils.settings import DATABASE_URL


class Database:
    def __init__(self, url: str | None = None):
        self.engine = create_engine(url or DATABASE_URL)
        self._connection = None

    def _get_connection(self):
        if self._connection is None or self._connection.closed:
            self._connection = self.engine.connect()
        return self._connection

    def get(self, key: str | bytes) -> dict:
        if isinstance(key, bytes):
            key = key.decode()
        key_parts = key.split("-", 1)
        if len(key_parts) != 2:
            return {}
        phash, full_path = key_parts
        path_parts = full_path.rsplit("/", 1)
        if len(path_parts) != 2:
            return {}
        path, name = path_parts
        query = text("SELECT path, name, phash, width, height, size FROM images WHERE phash = :phash AND path = :path AND name = :name")
        with self.engine.connect() as conn:
            result = conn.execute(query, {"phash": phash, "path": path, "name": name}).fetchone()
        if result:
            return {
                "path": result[0],
                "name": result[1],
                "phash": result[2],
                "width": result[3],
                "height": result[4],
                "size": result[5],
            }
        return {}

    def all(self, pattern: str = "*") -> list:
        query = text("SELECT path, name, phash, width, height, size FROM images")
        with self.engine.connect() as conn:
            results = conn.execute(query).fetchall()
        return [
            {
                "path": row[0],
                "name": row[1],
                "phash": row[2],
                "width": row[3],
                "height": row[4],
                "size": row[5],
            }
            for row in results
        ]

    def duplicates(self) -> dict[str, list]:
        duplicates = defaultdict(list)
        for item in self.all():
            if item["phash"]:
                duplicates[item["phash"]].append(item)
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def create(
        self,
        path: str,
        name: str,
        phash: str | None = None,
        width: int | None = None,
        height: int | None = None,
        size: int | None = None,
    ):
        query = text(
            "INSERT INTO images (path, name, phash, width, height, size) VALUES (:path, :name, :phash, :width, :height, :size)"
        )
        with self.engine.connect() as conn:
            conn.execute(query, {
                "path": path,
                "name": name,
                "phash": phash,
                "width": width,
                "height": height,
                "size": size,
            })
            conn.commit()

    def delete(self, path: str, name: str):
        query = text("DELETE FROM images WHERE path = :path AND name = :name")
        with self.engine.connect() as conn:
            conn.execute(query, {"path": path, "name": name})
            conn.commit()