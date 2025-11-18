import os
import sqlite3
from typing import List, Dict, Optional
import faiss
import numpy as np
import pickle
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
FAISS_INDEX_PATH = DATA_DIR / "faiss.index"
META_DB_PATH = DATA_DIR / "meta.db"

EMBED_DIM = 768  # change if your embedding model returns different dim

# SQLite metadata for chunks
def init_meta_db():
    conn = sqlite3.connect(META_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER,
            doc_name TEXT,
            page_info TEXT,
            text TEXT,
            embedding_id INTEGER,
            UNIQUE(doc_name, chunk_id)
        )
    """)
    conn.commit()
    conn.close()

# FAISS index helper
class FaissIndex:
    def __init__(self, dim=EMBED_DIM, path=FAISS_INDEX_PATH):
        self.dim = dim
        self.path = path
        self.index = None
        self._load_or_init()

    def _load_or_init(self):
        if self.path.exists():
            try:
                self.index = faiss.read_index(str(self.path))
            except Exception:
                # fallback: create new
                self.index = faiss.IndexFlatIP(self.dim)
        else:
            # Inner product index for cosine if we normalize embeddings
            self.index = faiss.IndexFlatIP(self.dim)

    def save(self):
        faiss.write_index(self.index, str(self.path))

    def add(self, vectors: np.ndarray):
        # vectors shape: (n, dim)
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)
        self.index.add(vectors)
        self.save()

    def search(self, q: np.ndarray, top_k=5):
        if q.dtype != np.float32:
            q = q.astype(np.float32)
        D, I = self.index.search(q, top_k)
        return D, I

    def reset(self):
        self.index = faiss.IndexFlatIP(self.dim)
        self.save()

# utility to insert chunk metadata and maintain mapping (embedding_id == rowid in faiss order)
def insert_chunks_meta(chunks: List[Dict], doc_name: str):
    conn = sqlite3.connect(META_DB_PATH)
    cur = conn.cursor()
    for idx, c in enumerate(chunks):
        cur.execute("""
            INSERT OR IGNORE INTO chunks (chunk_id, doc_name, page_info, text, embedding_id)
            VALUES (?,?,?,?,?)
        """, (c.get("id"), doc_name, c.get("page_info", ""), c["chunk"], None))
    conn.commit()
    conn.close()

def update_embedding_ids(embedding_ids: List[int], doc_name: str):
    """
    embedding_ids: list of embedding index positions assigned in FAISS in same order as docs inserted
    """
    conn = sqlite3.connect(META_DB_PATH)
    cur = conn.cursor()
    # naive update: set embedding_id for the newest entries for this doc in insertion order
    cur.execute("SELECT id FROM chunks WHERE doc_name=? ORDER BY id ASC", (doc_name,))
    rows = cur.fetchall()
    for row, e_id in zip(rows, embedding_ids):
        db_id = row[0]
        cur.execute("UPDATE chunks SET embedding_id=? WHERE id=?", (int(e_id), int(db_id)))
    conn.commit()
    conn.close()

def query_meta_by_embedding_ids(ids: List[int]) -> List[Dict]:
    conn = sqlite3.connect(META_DB_PATH)
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"SELECT chunk_id, doc_name, page_info, text, embedding_id FROM chunks WHERE embedding_id IN ({placeholders})", ids)
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "chunk_id": r[0],
            "doc_name": r[1],
            "page_info": r[2],
            "text": r[3],
            "embedding_id": r[4]
        })
    return results

def clear_all():
    if META_DB_PATH.exists():
        os.remove(META_DB_PATH)
    if FAISS_INDEX_PATH.exists():
        os.remove(FAISS_INDEX_PATH)
    init_meta_db()
    # create empty faiss
    fi = FaissIndex()
    fi.reset()
