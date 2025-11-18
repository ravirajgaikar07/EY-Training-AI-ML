from typing import List, Tuple, Dict, Optional
from .db import FaissIndex, query_meta_by_embedding_ids
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
import numpy as np
import os
import faiss
from ingest import embedding_model
from utils import clean_text

llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")

FAQ_INDEX_PATH = "faiss_indexes/faq.index"
MANUAL_INDEX_PATH = "faiss_indexes/manual.index"

def load_or_create_index(path, dim):
    if os.path.exists(path):
        return faiss.read_index(path)
    return faiss.IndexFlatL2(dim)

DIM = 768
FAQ_INDEX = load_or_create_index(FAQ_INDEX_PATH, DIM)
MANUAL_INDEX = load_or_create_index(MANUAL_INDEX_PATH, DIM)

INTENT_TEMPLATES = {
    "faq": [
        "I have a question about how something works",
        "What is the process for",
        "How does this work",
        "Where can I find information"
    ],
    "troubleshooting": [
        "My device shows an error",
        "I am seeing an error code",
        "The app crashed",
        "It is not working",
        "Cannot connect to WiFi",
        "how to fix"
    ],
    "billing": [
        "I was charged incorrectly",
        "billing issue",
        "refund",
        "invoice",
        "payment failed"
    ],
    "cancellation": [
        "cancel my subscription",
        "how to cancel",
        "terminate my account",
        "stop my plan"
    ],
}

TEMPLATE_EMBS = {}
for intent, templates in INTENT_TEMPLATES.items():
    emb_list = []
    for t in templates:
        cleaned = clean_text(t)
        vec = np.array(
            embedding_model.embed_query(cleaned),
            dtype="float32"
        ).reshape(-1)
        emb_list.append(vec)

    TEMPLATE_EMBS[intent] = np.vstack(emb_list)

class IntentRouter:

    @staticmethod
    def _cos_sim(a: np.ndarray, b: np.ndarray) -> float:
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        return float(np.dot(a, b) / denom) if denom > 0 else 0.0

    async def route(self, query: str) -> Tuple[str, float]:
        q = clean_text(query)
        q_emb = np.array(
            embedding_model.embed_query(q),
            dtype="float32"
        ).reshape(-1)

        best_intent = "unknown"
        best_score = 0.0

        for intent, emb_matrix in TEMPLATE_EMBS.items():
            sims = [self._cos_sim(q_emb, emb_matrix[i]) for i in range(emb_matrix.shape[0])]
            intent_score = max(sims)

            if intent_score > best_score:
                best_score = intent_score
                best_intent = intent

        if best_score < 0.62:
            return "unknown", best_score

        return best_intent, best_score

# RAG FAQ agent
class RAGFAQAgent:
    def __init__(self, llm):
        self.llm = llm
        self.faiss = faiss_index

    def retrieve_context(self, query: str, top_k=4, min_score=0.3):
        # embed query
        q_emb = embedding_model.embed_query(query)
        qv = np.array([q_emb], dtype=np.float32)
        qv = qv / (np.linalg.norm(qv, axis=1, keepdims=True) + 1e-10)
        D, I = self.faiss.search(qv, top_k)
        D = D.tolist()[0]
        I = I.tolist()[0]
        # filter by min_score
        filtered = []
        for score, idx in zip(D, I):
            if score >= min_score and idx >= 0:
                filtered.append((idx, float(score)))
        if not filtered:
            return []
        ids = [int(x[0]) for x in filtered]
        metas = query_meta_by_embedding_ids(ids)
        # sort by score mapping
        return metas

    def answer(self, query: str):
        ctx = self.retrieve_context(query)
        if not ctx:
            return {
                "answer": "The uploaded document does not contain the requested information.",
                "sources": [],
                "confidence": 0.0
            }
        # build grounded prompt
        # include top chunks with source markers, instruct no hallucination
        prompt_parts = []
        for i, c in enumerate(ctx):
            snippet = c["text"][:1000]
            prompt_parts.append(f"[[source:{c['doc_name']}#chunk:{c['chunk_id']}]]\n{snippet}\n")
        prompt = (
            "You are a highly reliable assistant answering precisely only from the supplied sources.\n"
            "Do NOT make up facts. If the answer is not present in the sources, say exactly: "
            "\"The uploaded document does not contain the requested information.\".\n\n"
            "Sources:\n" + "\n".join(prompt_parts) + "\n\n"
            f"Question: {query}\nAnswer succinctly and cite sources in brackets like [source:filename#chunk:ID]."
        )
        resp = self.llm.generate([{"role":"user","content":prompt}])
        # the response object shape depends on provider; adapt to text extraction
        text = ""
        try:
            # if langchain output
            text = resp.generations[0][0].text
        except Exception:
            try:
                text = resp[0].text
            except Exception:
                text = str(resp)
        sources = [f"{c['doc_name']}#chunk:{c['chunk_id']}" for c in ctx]
        return {"answer": text.strip(), "sources": sources, "confidence": 0.9}

# Troubleshooter Agent: multi-step
class TroubleshooterAgent:
    def __init__(self):
        self.state = {}  # per-conversation state; in real system this should persist

    def start_flow(self, convo_id: str, initial_query: str):
        # seed state
        self.state[convo_id] = {
            "steps": [],
            "done": False,
            "last_question": "What error code do you see (if any)?",
            "context": initial_query
        }
        return {"question": self.state[convo_id]["last_question"], "done": False}

    def step(self, convo_id: str, answer: str):
        st = self.state.get(convo_id)
        if not st:
            return {"question": "Session not found. Start again.", "done": True}
        st["steps"].append({"question": st["last_question"], "answer": answer})
        # decision tree example
        q_lower = answer.lower()
        if "no error" in q_lower or "none" in q_lower:
            st["last_question"] = "Is the device connected to WiFi?"
            return {"question": st["last_question"], "done": False}
        if "wifi" in st["last_question"].lower():
            if "yes" in q_lower:
                st["last_question"] = "Can you try restarting the application and tell me if the issue persists?"
                return {"question": st["last_question"], "done": False}
            else:
                st["last_question"] = "Please connect the device to WiFi and retry. Did it work?"
                return {"question": st["last_question"], "done": False}
        if "restart" in st["last_question"].lower():
            if "yes" in q_lower and ("works" in q_lower or "fixed" in q_lower or "resolved" in q_lower):
                st["done"] = True
                return {"question": "Glad it worked. Anything else I can help with?", "done": True}
            else:
                st["last_question"] = "Please provide the exact error message or a screenshot (describe it)."
                return {"question": st["last_question"], "done": False}
        # fallback end
        st["done"] = True
        return {"question": "I couldn't resolve. Escalate to human? (yes/no)", "done": False, "suggest_escalation": True}

    def get_steps(self, convo_id: str):
        return self.state.get(convo_id, {}).get("steps", [])

# Supervisor (Human-in-loop Escalation evaluator)
class EscalationSupervisor:
    def __init__(self, threshold_low_conf=0.4, max_failed_steps=3):
        self.threshold_low_conf = threshold_low_conf
        self.max_failed_steps = max_failed_steps

    def evaluate(self, convo_history: List[dict], latest_agent_output: Dict, retrieval_confidence: float=False):
        # simple heuristics: repeated negative feedback or low retrieval_confidence triggers escalation
        failures = 0
        for msg in convo_history:
            if msg.get("user_feedback") == "unsatisfied" or msg.get("attempt") == "failed":
                failures += 1
        escalate = False
        reason = ""
        if retrieval_confidence and retrieval_confidence < self.threshold_low_conf:
            escalate = True
            reason = f"Low retrieval confidence: {retrieval_confidence}"
        if failures >= self.max_failed_steps:
            escalate = True
            reason = reason or f"{failures} failed attempts"
        if latest_agent_output.get("escalate") or latest_agent_output.get("suggest_escalation"):
            escalate = True
            reason = reason or "Agent suggested escalation"

        if not escalate:
            return {"escalate": False}
        # assemble history in text (or structured)
        history_text = "\n".join([f"{m.get('role','user')}: {m.get('text','')}" for m in convo_history])
        return {
            "escalate": True,
            "reason": reason,
            "history": history_text,
            "agent_notes": latest_agent_output.get("notes", "")
        }

# Ticketing Agent
class TicketingAgent:
    def __init__(self):
        pass

    def create_ticket(self, user_query: str, troubleshooting_steps: List[str], meta: dict):
        ticket = {
            "user_query": user_query,
            "retrieved_refs": retrieved_refs,
            "troubleshooting_steps": troubleshooting_steps,
            "meta": meta
        }
        # placeholder for integration
        self.raise_ticket(ticket)
        return ticket

    def raise_ticket(self, ticket: dict):
        # intentionally empty - ready to integrate with CRM / ticketing APIs
        # e.g., POST to zendesk/freshdesk/jira here
        return None
