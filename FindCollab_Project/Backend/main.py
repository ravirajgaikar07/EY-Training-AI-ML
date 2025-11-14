# Imports
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
import sqlite3
import numpy as np
import os
import faiss
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# --------------------------
# Logging Setup
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --------------------------
# App + Config
# --------------------------
load_dotenv()
app = FastAPI()
logger.info("FastAPI server booting...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Database Connection
# --------------------------
try:
    DB_PATH = "creator_ai.db"
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    conn.commit()
    logger.info("Database connected.")
except Exception as e:
    logger.error(f"DB Connection failed: {e}")
    raise e

# --------------------------
# Embeddings Model
# --------------------------
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

FAISS_INDEX_PATH = "creators_index.faiss"
dimension = 768

# --------------------------
# Creator Schema
# --------------------------
class CreatorEnroll(BaseModel):
    display_name: str
    user_name: str
    email: str
    phone_number: str
    niches: str
    category: str
    followers_count: int
    audience_geography: str
    reel_engagement: float
    post_engagement: float
    story_engagement: float
    external_linktap: float

# --------------------------
# FAISS Init
# --------------------------
try:
    if os.path.exists(FAISS_INDEX_PATH):
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        logger.info("Loaded FAISS index.")
    else:
        faiss_index = faiss.IndexFlatL2(dimension)
        logger.info("Created new FAISS index.")
except Exception as e:
    logger.error(f"FAISS load error: {e}")
    raise e

# --------------------------
# Helper: Normalize Embeddings
# --------------------------
def normalize_embeddings(vec):
    norm = np.linalg.norm(vec, axis=1, keepdims=True)
    return vec / norm

# --------------------------
# Helper: Fetch Creators
# --------------------------
def fetch_creators_with_embeddings():
    try:
        cursor.execute("""
            SELECT creator_id, display_name, user_name, niches, category, audience_geography,
                reel_engagement, post_engagement, story_engagement, external_linktap,
                followers_count, embedding
            FROM creators
            WHERE embedding IS NOT NULL AND embedding != ''
        """)
        rows = cursor.fetchall()

        creators = []
        for r in rows:
            emb = json.loads(r[-1]) if r[-1] else {}
            faiss_id = emb.get("faiss_id")
            creators.append((*r[:-1], faiss_id))

        return creators
    except Exception as e:
        logger.error(f"Fetch creators failed: {e}")
        return []

# --------------------------
# Brief Refinement
# --------------------------
def refine_brief_with_gemini(brief: str) -> str:
    try:
        prompt = f"""
        You are an AI marketing strategist.
        The following is a campaign brief:
        {brief}
        Summarize it in one short sentence.
        """

        llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")
        response = llm_model.generate([prompt])
        refined = response.generations[0][0].text.strip()

        logger.info(f"Refined brief: {refined}")
        return refined
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return brief  # fallback

# --------------------------
# Text Embedding
# --------------------------
def embed_text(text: str):
    try:
        logger.info("Generating embedding...")
        vector = embedding_model.embed_query(text)
        return np.array(vector, dtype="float32")
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

# --------------------------
# Why Creator Fits
# --------------------------
def why_creator_fits(creator: tuple, brand_brief: str, similarity_score: float) -> str:
    llm = GoogleGenerativeAI(model="gemini-2.0-flash")

    prompt = f"""
Explain in 2–3 crisp sentences why this creator is a strong match.
Brand brief: {brand_brief}
Creator: {creator[1]} (@{creator[2]})
Match Score: {similarity_score}%
"""

    try:
        response = llm.generate([prompt])
        text = response.generations[0][0].text.strip()
        return " ".join(text.split())
    except Exception as e:
        logger.error(f"Why-fit LLM error ({creator[1]}): {e}")
        return (
            f"{creator[1]} (@{creator[2]}) matches strongly ({similarity_score}%). "
            f"Strong engagement in {creator[5]} and niche {creator[3]} fits the brand."
        )

# --------------------------
# Send Email
# --------------------------
def send_email(to_email, subject, body):
    try:
        logger.info(f"Sending email to {to_email}")

        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "")
        sender_password = os.getenv("SENDER_PASSWORD", "")

        # Simulate mode
        if not sender_email:
            logger.warning("⚠ SMTP not configured — email simulated")
            return True

        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        logger.error(f"Email error: {e}")
        return False

# --------------------------
# Similarity Search
# --------------------------
def find_similar_creators(query_vector, brand_brief, top_k=5):
    try:
        if faiss_index.ntotal == 0:
            raise HTTPException(status_code=500, detail="FAISS index empty.")

        logger.info("Running similarity search...")
        D, I = faiss_index.search(np.array([query_vector], dtype="float32"), top_k)

        creators = fetch_creators_with_embeddings()
        faiss_map = {c[-1]: c for c in creators}

        results = []

        for rank, idx in enumerate(I[0]):
            c = faiss_map.get(idx)
            if not c:
                continue

            distance = D[0][rank]
            similarity = 1 - (distance ** 2) / 2
            similarity_score = max(0, min(round(similarity * 100, 2), 100))

            reason = str(why_creator_fits(c, brand_brief, similarity_score))

            results.append({
                "rank": rank + 1,
                "display_name": c[1],
                "user_name": c[2],
                "matching_percentage": similarity_score,
                "niches": c[3],
                "why_fit": reason
            })

        return results
    except Exception as e:
        logger.error(f"Similarity search error: {e}")
        raise

# --------------------------
# API: Match Creators
# --------------------------
@app.post("/match_creators")
def match_creators(input_data: dict):
    try:
        logger.info("/match_creators called")

        brief = input_data.get("brief")
        if not brief:
            raise HTTPException(status_code=400, detail="Missing 'brief'.")

        refined = refine_brief_with_gemini(brief)
        vector = embed_text(refined)
        results = find_similar_creators(vector, refined, top_k=5)

        return {"matches": results}

    except Exception as e:
        logger.error(f"match_creators failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------
# API: Enroll Creator
# --------------------------
@app.post("/enroll_creator")
async def enroll_creator(data: CreatorEnroll):
    try:
        logger.info(f"Enrolling creator: {data.display_name}")

        combined_text = (
            f"{data.display_name} {data.user_name} {data.niches} "
            f"{data.category} {data.followers_count} {data.audience_geography} "
        )

        embedding = embedding_model.embed_query(combined_text)
        vec_np = normalize_embeddings(np.array(embedding).astype("float32").reshape(1, -1))

        faiss_index.add(vec_np)
        faiss_id = faiss_index.ntotal - 1
        embedding_id = json.dumps({"faiss_id": faiss_id})

        cursor.execute("""
            INSERT INTO creators 
            (display_name, user_name, email, phone_number, niches, category,
             followers_count, audience_geography, reel_engagement, post_engagement,
             story_engagement, external_linktap, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.display_name, data.user_name, data.email, data.phone_number,
            data.niches, data.category, data.followers_count, data.audience_geography,
            data.reel_engagement, data.post_engagement, data.story_engagement,
            data.external_linktap, embedding_id
        ))

        conn.commit()
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)

        logger.info(f"Creator enrolled: {data.display_name}")
        return {"message": "Creator enrolled", "creator_id": cursor.lastrowid}

    except Exception as e:
        logger.error(f"enroll_creator failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------
# API: Send Email
# --------------------------
@app.post("/send_creator_email")
def send_creator_email(request: dict):
    try:
        logger.info("/send_creator_email called")

        user_name = request.get("user_name")
        brand_name = request.get("brand_name")
        brand_brief = request.get("brand_brief")

        if not user_name or not brand_name or not brand_brief:
            raise HTTPException(status_code=400, detail="Missing required fields.")

        cursor.execute("SELECT email, display_name FROM creators WHERE user_name = ?", (user_name,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Creator not found")

        receiver_email = row[0]
        receiver_name=row[1]

        prompt = f"""Write a clean, simple HTML email. We at Collab Finder have discovered a 
        collaboration opportunity for the creator {receiver_name}. The brand is {brand_name}. 
        Use the following brand information to write the email in a clear, engaging, and professional tone:
        Brand Brief: {brand_brief}
        Structure the email like this:
        Address the creator by name.
        Explain that Collab Finder found a potential collaboration opportunity for them.
        Introduce the brand and summarize the brand brief naturally.
        Explain why this opportunity is relevant or valuable for the creator (you can infer based on typical creator-brand alignment).
        Invite them for a short call to explore the opportunity.
        Close the email professionally.
        End the email with:
        Sincerely,
        Collab Finder
        Do NOT include anything after the signature.
        Do NOT add explanations or markdown — output ONLY clean HTML.
        """
        llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")
        response = llm_model.generate([prompt])
        html_body = response.generations[0][0].text.strip()
        html_body=html_body[7:-3]
        print(html_body)
        status = send_email(receiver_email, f"Collaboration with {brand_name}", html_body)

        return {
            "sent_to": receiver_email,
            "status": "sent" if status else "failed"
        }

    except Exception as e:
        logger.error(f"send_creator_email failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

