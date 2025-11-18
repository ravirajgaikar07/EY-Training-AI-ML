import sqlite3
import uuid
from typing import List, Dict
DB_PATH = "tickets.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            problem_summary TEXT,
            solution_summary TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()

