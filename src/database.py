import sqlite3
import json
import os

def init_db(db_path="fingerprints.db"):
    """Initializes the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fingerprints (
            id TEXT PRIMARY KEY,
            image_path TEXT,
            template TEXT
        )
    ''')
    conn.commit()
    return conn

def store_fingerprint(conn, fp_id, image_path, template):
    """Stores fingerprint data in the database."""
    cursor = conn.cursor()
    # Convert template (list of dicts) to JSON string
    template_json = json.dumps(template)
    cursor.execute('''
        INSERT OR REPLACE INTO fingerprints (id, image_path, template)
        VALUES (?, ?, ?)
    ''', (fp_id, image_path, template_json))
    conn.commit()
