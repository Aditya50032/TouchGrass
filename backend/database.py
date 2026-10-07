import json
import sqlite3
from contextlib import contextmanager
from .config import DATA_DIR

DATABASE_PATH = DATA_DIR / 'traillens.db'

@contextmanager
def connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()

def init_db():
    with connect() as connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS discoveries (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, confidence TEXT NOT NULL, description TEXT NOT NULL, facts TEXT NOT NULL, outdoor_challenge TEXT NOT NULL, image_filename TEXT NOT NULL, xp_awarded INTEGER NOT NULL DEFAULT 50, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

def save_discovery(discovery, image_filename, xp_awarded):
    with connect() as connection:
        cursor = connection.execute('INSERT INTO discoveries (name,category,confidence,description,facts,outdoor_challenge,image_filename,xp_awarded) VALUES (?,?,?,?,?,?,?,?)', (discovery['name'], discovery['category'], discovery['confidence'], discovery['description'], json.dumps(discovery['facts']), discovery['outdoor_challenge'], image_filename, xp_awarded))
        row = connection.execute('SELECT * FROM discoveries WHERE id = ?', (cursor.lastrowid,)).fetchone()
    return serialize(row)

def list_discoveries():
    with connect() as connection:
        rows = connection.execute('SELECT * FROM discoveries ORDER BY id DESC').fetchall()
    return [serialize(row) for row in rows]

def get_discovery(discovery_id):
    with connect() as connection:
        row = connection.execute('SELECT * FROM discoveries WHERE id = ?', (discovery_id,)).fetchone()
    return serialize(row) if row else None

def get_stats():
    with connect() as connection:
        row = connection.execute('SELECT COUNT(*) AS discoveries, COALESCE(SUM(xp_awarded),0) AS total_xp FROM discoveries').fetchone()
    return {'discoveries': row['discoveries'], 'total_xp': row['total_xp']}

def serialize(row):
    result = dict(row)
    result['facts'] = json.loads(result['facts'])
    return result
