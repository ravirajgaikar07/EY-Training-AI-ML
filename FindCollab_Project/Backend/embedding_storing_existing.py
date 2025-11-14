from fastapi import FastAPI, HTTPException
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import sqlite3
import numpy as np
import os
import faiss
import json
from pydantic import BaseModel
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
load_dotenv()
app = FastAPI()

DB_PATH = "creator_ai.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
conn.commit()
print("✅ Database ready.")

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
FAISS_INDEX_PATH = "creators_index.faiss"
dimension = 768

class CreatorEnroll(BaseModel):
    creator_id: int
    display_name: str
    user_name: str
    email: str
    phone_number: str
    niches: str
    category: str
    audience_geography: str
    reel_engagement: float
    post_engagement: float
    story_engagement: float
    external_linktap: float

# FAISS Load/Create
if os.path.exists(FAISS_INDEX_PATH):
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    print("✅ Loaded existing FAISS index.")
else:
    faiss_index = faiss.IndexFlatL2(dimension)
    print("🆕 Created new FAISS index.")

# ---------------- FUNCTIONS ----------------
def normalize_embeddings(vec):
    norm = np.linalg.norm(vec, axis=1, keepdims=True)
    return vec / norm

def fetch_unembedded_creators():
    cursor.execute("SELECT * FROM creators WHERE embedding IS NULL OR embedding = ''")
    return cursor.fetchall()

def embed_and_store_creators():
    creators = fetch_unembedded_creators()
    if not creators:
        print("⚠️ No new creators found.")
        return 0

    for creator in creators:
        (creator_id, display_name, user_name, email, phone_number, niches, category,
         followers_count, audience_geography, reel_engagement, post_engagement,
         story_engagement, external_linktap, embedding) = creator

        combined_text = (
            f"Niche: {niches}. "
            f"Category: {category}. "
            f"Follower Count: {followers_count}. "
            f"Audience Geography: {audience_geography}. "
            f"Reel Engagement: {reel_engagement}. "
            f"Post Engagement: {post_engagement}. "
            f"Story Engagement: {story_engagement}. "
            f"Linktap: {external_linktap}. "
        )

        try:
            vector = embedding_model.embed_query(combined_text)
            vec_np = np.array([vector], dtype="float32")
            vec_np = normalize_embeddings(vec_np)
            faiss_index.add(vec_np)
            faiss_id = faiss_index.ntotal - 1

            cursor.execute(
                "UPDATE creators SET embedding = ? WHERE creator_id = ?",
                (json.dumps({"faiss_id": faiss_id}), creator_id)
            )
            conn.commit()
        except Exception as e:
            print(f"❌ Error embedding creator {display_name}: {e}")

    faiss.write_index(faiss_index, FAISS_INDEX_PATH)
    print(f"✅ Successfully embedded {len(creators)} creators.")
    return len(creators)

# ---------------- API ----------------
@app.get("/process_creators")
def process_creators():
    count = embed_and_store_creators()
    return {"processed_creators": count, "message": "Embeddings stored successfully."}


















