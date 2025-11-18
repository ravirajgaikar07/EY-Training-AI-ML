import json
import numpy as np
from langchain_google_genai import GoogleGenerativeAI
from .ingest import FAQ_INDEX, FAQ_METADATA, embedding_model

llm = GoogleGenerativeAI(model="gemini-2.0-flash")

TOP_K = 4
MIN_SCORE = 0.30


def retrieve_faq_context(query: str, top_k=TOP_K, min_score=MIN_SCORE):
    q_emb = embedding_model.embed_query(query)
    qv = np.array([q_emb], dtype="float32")
    qv /= (np.linalg.norm(qv) + 1e-10)

    # FAISS search
    scores, ids = FAQ_INDEX.search(qv, top_k)
    scores = scores[0]
    ids = ids[0]

    results = []
    for idx, score in zip(ids, scores):
        if idx < 0 or score < min_score:
            continue
        chunk_meta = FAQ_METADATA[idx]
        results.append({
            "text": chunk_meta["text"],
            "score": float(score)
        })

    return results



def answer(query: str):
    ctx = retrieve_faq_context(query)

    if not ctx:
        return {
            "answer": "The FAQ repository does not contain information about this query."
        }

    # Build context prompt
    source_texts = []
    for i, item in enumerate(ctx):
        snippet = item["text"][:700]  # safety trim
        source_texts.append(f"[chunk {i}]\n{snippet}\n")

    prompt = (
        "You are a strict, factual assistant. Answer ONLY using information from the provided FAQ sources.\n"
        "If the answer is not present in the sources, reply exactly:\n"
        "\"The FAQ repository does not contain information about this query.\"\n\n"
        "FAQ Sources:\n" +
        "\n".join(source_texts) +
        "\n\nQuestion: " + query + "\n"
        "Answer with the facts only and cite chunks like [chunk 0], [chunk 1]."
    )

    # LLM call
    resp = llm_model.generate([prompt])
    text = resp.generations[0][0].text.strip()

    return {
        "answer": text
    }
