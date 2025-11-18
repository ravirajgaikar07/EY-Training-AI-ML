import os
import io
import json
import faiss
import numpy as np
from fastapi import UploadFile
from typing import List
from pypdf import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .utils import chunk_text

from dotenv import load_dotenv
import os
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Ensure directory exists
os.makedirs("faiss_indexes", exist_ok=True)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

DIM = 768

# Paths
FAQ_INDEX_PATH = "faiss_indexes/faq.index"
MANUAL_INDEX_PATH = "faiss_indexes/manual.index"
FAQ_META_PATH = "faiss_indexes/faq_meta.json"
MANUAL_META_PATH = "faiss_indexes/manual_meta.json"


def load_or_create_index(path, dim):
    if os.path.exists(path):
        return faiss.read_index(path)
    return faiss.IndexFlatL2(dim)


FAQ_INDEX = load_or_create_index(FAQ_INDEX_PATH, DIM)
MANUAL_INDEX = load_or_create_index(MANUAL_INDEX_PATH, DIM)

FAQ_METADATA = json.load(open(FAQ_META_PATH)) if os.path.exists(FAQ_META_PATH) else []
MANUAL_METADATA = json.load(open(MANUAL_META_PATH)) if os.path.exists(MANUAL_META_PATH) else []


def save_all():
    faiss.write_index(FAQ_INDEX, FAQ_INDEX_PATH)
    faiss.write_index(MANUAL_INDEX, MANUAL_INDEX_PATH)

    json.dump(FAQ_METADATA, open(FAQ_META_PATH, "w"))
    json.dump(MANUAL_METADATA, open(MANUAL_META_PATH, "w"))


# -------- TEXT EXTRACTORS -------- #

def extract_text_from_pdf(raw_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw_bytes))
    text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text.append(page_text)
    return "\n".join(text)


async def extract_txt_text(file: UploadFile) -> str:
    raw = await file.read()
    return raw.decode("utf-8", errors="ignore")


# -------- INGESTION FUNCTIONS -------- #

async def ingest_and_store_embeddings_FAQ(files: List[UploadFile]):
    for file in files:
        raw = await file.read()
        text = extract_text_from_pdf(raw)

        chunks = chunk_text(text)

        for c in chunks:
            text_chunk = c["chunk"]

            emb = np.array(
                embedding_model.embed_query(text_chunk),
                dtype="float32"
            ).reshape(1, -1)

            FAQ_INDEX.add(emb)
            FAQ_METADATA.append({
                "text": text_chunk
            })

    save_all()
    print("Saved ---------")


async def ingest_and_store_embeddings_Manual(files: List[UploadFile]):
    for file in files:
        raw = await file.read()
        text = raw.decode("utf-8", errors="ignore")

        chunks = chunk_text(text)

        for c in chunks:
            text_chunk = c["chunk"]

            emb = np.array(
                embedding_model.embed_query(text_chunk),
                dtype="float32"
            ).reshape(1, -1)

            MANUAL_INDEX.add(emb)
            MANUAL_METADATA.append({
                "text": text_chunk
            })

    save_all()
