import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT / "data" / "traillens.db"


def init_db() -> None:
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence TEXT NOT NULL,
                description TEXT NOT NULL,
                facts TEXT NOT NULL,
                outdoor_challenge TEXT NOT NULL,
                image_filename TEXT NOT NULL,
                xp_awarded INTEGER NOT NULL DEFAULT 25,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@contextmanager
def connect():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def create_discovery(discovery: dict, image_filename: str, xp_awarded: int = 25) -> dict:
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO discoveries
            (name, category, confidence, description, facts, outdoor_challenge, image_filename, xp_awarded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (discovery["name"], discovery["category"], discovery["confidence"],
             discovery["description"], json.dumps(discovery["facts"]),
             discovery["outdoor_challenge"], image_filename, xp_awarded),
        )
        row = connection.execute("SELECT * FROM discoveries WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return serialize(row)


def list_discoveries() -> list[dict]:
    with connect() as connection:
        rows = connection.execute("SELECT * FROM discoveries ORDER BY id DESC").fetchall()
    return [serialize(row) for row in rows]


def stats() -> dict:
    with connect() as connection:
        row = connection.execute("SELECT COUNT(*) AS discoveries, COALESCE(SUM(xp_awarded), 0) AS xp FROM discoveries").fetchone()
    return {"discoveries": row["discoveries"], "xp": row["xp"]}


def serialize(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["facts"] = json.loads(result["facts"])
    return result
