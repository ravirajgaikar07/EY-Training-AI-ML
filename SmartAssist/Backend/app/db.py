import sqlite3
from .logger import logger

DB_PATH = "tickets.db"

def init_db():
    try:
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
        logger.info("Database initialized successfully at %s", DB_PATH)
    except Exception as e:
        logger.error("Error initializing database: %s", str(e))
