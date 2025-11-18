from typing import List, Tuple, Dict, Optional
from .db import init_db
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from .ingest import FAQ_METADATA, MANUAL_METADATA, embedding_model
import numpy as np
import os
import faiss
import time
import sqlite3
import uuid

llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")

FAQ_INDEX_PATH = "faiss_indexes/faq.index"
MANUAL_INDEX_PATH = "faiss_indexes/manual.index"
DB_PATH = "tickets.db"

def load_or_create_index(path, dim):
    if os.path.exists(path):
        return faiss.read_index(path)
    return faiss.IndexFlatL2(dim)

DIM = 768
FAQ_INDEX = load_or_create_index(FAQ_INDEX_PATH, DIM)
MANUAL_INDEX = load_or_create_index(MANUAL_INDEX_PATH, DIM)

# Intent Classifier
class IntentRouter:
    def __init__(self):
        pass

    def answer(self, query: str, history: str) -> str:
        prompt = f"""
    You are an extremely strict INTENT CLASSIFIER.

    You must choose EXACTLY ONE label from the following:

    ------------------------------------------------------------
    VALID LABELS:
    1. faq            → general questions, how-to, product info, explanations
    2. troubleshoot   → errors, malfunctions, app/device not working, technical issues
    3. escalation     → user frustration OR unclear OR no answer possible
    ------------------------------------------------------------

    ### Rules for Classification ###

    #### 1. FAQ
    Choose **faq** ONLY IF:
    - The user asks for general information
    - "What is…", "How does it work?", "Explain…", "Where can I find…"
    - No sign of errors or frustration
    - User is calm and asking informational questions

    #### 2. Troubleshoot
    Choose **troubleshoot** when:
    - User reports any error, bug, malfunction, failure
    - “App crashed”, “Not working”, “Error code”, “Cannot login”, “Device won't start”
    - There is a technical issue that needs guided diagnosis

    #### 3. Escalation
    Choose **escalation** when:
    - The system cannot fulfill the request
    - User is frustrated, angry, or repeating questions
    - History shows unresolved attempts
    - User says things like:
      “This is not helping”, “You already asked this”, “I want a human”, “You are useless”
    - The query is unclear, ambiguous, or does not match faq/troubleshoot
    - You are unsure → **always escalate**

    ------------------------------------------------------------
    INPUTS PROVIDED TO YOU

    User Query:
    {query}

    Chat History (most recent first):
    {history}

    ------------------------------------------------------------

    Return ONLY ONE word:
    faq, troubleshoot, or escalation.
    """
        try:
            llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")
            response = llm_model.generate([prompt])
            refined = response.generations[0][0].text.strip()
            return refined
        except Exception as e:
            print(e)
            return "escalation"

    async def route(self,conversation_history: List[dict]) -> dict:
        last_msgs = conversation_history[-10:]
        parts = []
        for m in last_msgs:
            role = "User" if m["role"] == "user" else "Agent"
            parts.append(f"{role}: {m['text']}")
        history = "\n".join(parts)
        last_user_msgs = [m for m in reversed(conversation_history) if m["role"] == "user"]
        if last_user_msgs:
            query = last_user_msgs[0]["text"]
        else:
            query = ""
        intent = self.answer(query,history)
        if "faq" in intent:
            return {"answer":"faq"}
        elif "troubleshoot" in intent:
            return {"answer":"troubleshoot"}
        elif "escalation" in intent:
            return {"answer":"escalation"}

        return {"answer":"escalation"}

# RAG FAQ agent
class RAGFAQAgent:
    def __init__(self):
        pass

    def retrieve_faq_context(self, query: str, top_k=4, min_score=0.30):
        q_emb = embedding_model.embed_query(query)
        qv = np.array([q_emb], dtype="float32")
        qv /= (np.linalg.norm(qv) + 1e-10)

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

    def answer(self, history:List[dict]):
        latest_msg = [m for m in reversed(history) if m["role"] == "user"]
        query=latest_msg[0]["text"]
        ctx = self.retrieve_faq_context(query)

        if not ctx:
            return {
                "answer": "The FAQ repository does not contain information about this query."
            }

        # Format conversation history
        history_text = ""
        if history:
            for msg in history:
                role = msg.get("role", "")
                text = msg.get("text", "")
                history_text += f"{role.upper()}: {text}\n"
        else:
            history_text = "None\n"

        # Build FAQ context
        source_texts = []
        for i, item in enumerate(ctx):
            snippet = item["text"][:700]
            source_texts.append(f"[chunk {i}]\n{snippet}\n")

        # FINAL PROMPT
        prompt = (
            "You are a strict factual assistant.\n"
            "Use the conversation history ONLY to understand context.\n"
            "Use ONLY the FAQ sources for factual answers.\n"
            "If the FAQ does not contain the answer, reply exactly:\n"
            "\"The FAQ repository does not contain information about this query.\"\n\n"

            f"Conversation History:\n{history_text}\n"
            "FAQ Sources:\n"
            + "\n".join(source_texts)
            + "\n\nQuestion: " + query + "\n"
            "Answer strictly from FAQ sources and cite chunks like [chunk 0]."
        )

        # LLM call
        resp = llm_model.generate([{"role": "user", "content": prompt}])
        text = resp.generations[0][0].text.strip()

        return {
            "answer": text
        }

# Troubleshooter Agent: multi-step
class TroubleshooterAgent:
    def __init__(self):
        pass

    def retrieve_manual_context(self, query: str, top_k=4, min_score=0.30):
        q_emb = embedding_model.embed_query(query)
        qv = np.array([q_emb], dtype="float32")
        qv /= (np.linalg.norm(qv) + 1e-10)

        # FAISS search on MANUAL index
        scores, ids = MANUAL_INDEX.search(qv, top_k)
        scores = scores[0]
        ids = ids[0]

        results = []
        for idx, score in zip(ids, scores):
            if idx < 0 or score < min_score:
                continue
            chunk_meta = MANUAL_METADATA[idx]
            results.append({
                "text": chunk_meta["text"],
                "score": float(score)
            })

        return results

    def answer(self, history: List[dict]):
        # Extract latest user message
        latest_user_msgs = [m for m in reversed(history) if m.get("role") == "user"]
        if not latest_user_msgs:
            return {"answer": "No user message found in history.", "sources": [], "confidence": 0.0}

        query = latest_user_msgs[0]["text"]

        ctx = self.retrieve_manual_context(query)

        if not ctx:
            return {
                "answer": "The manual repository does not contain information about this query."
            }

        # Format conversation history (brief)
        history_text = ""
        for msg in history:
            role = msg.get("role", "")
            text = msg.get("text", "")
            history_text += f"{role.upper()}: {text}\n"

        source_texts = []
        for i, item in enumerate(ctx):
            snippet = item["text"][:700]   # limit text
            source_texts.append(f"[chunk {i}]\n{snippet}\n")

        # Enhanced prompt for stepwise troubleshooting
        prompt = (
            "You are a precise, conservative troubleshooting assistant. IMPORTANT: Answer ONLY using the provided manual sources.\n"
            "Do NOT invent or assume facts beyond the sources. If the steps below require information not in the manual, say exactly:\n"
            "\"The manual repository does not contain information required to perform this step.\"\n\n"

            "Task: Given the user's latest message and the conversation history, produce a clear, numbered, step-by-step troubleshooting plan that a support agent or an end user can follow.\n"
            "For each step include:\n"
            "  1) A short action to take (one sentence)\n"
            "  2) Estimated time to complete (e.g., 30s, 2 min)\n"
            "  3) Expected result or output after performing the step\n"
            "  4) If applicable, the exact command or UI path to follow (in code or bold text)\n"
            "  5) A clear next-step decision (if success -> stop and confirm; if not -> do step N+1)\n\n"
            "At the end, include:\n"
            "  - A one-line conclusion (resolved / escalate)\n"
            "  - If escalate, list exactly what to include in the ticket (short summary, steps tried, relevant chunk citations)\n\n"
            f"Conversation History (for context only):\n{history_text}\n"
            "Manual Sources (use them verbatim for facts):\n"
            + "\n".join(source_texts)
            + "\n\n"
            "Question: " + query + "\n\n"
        )
        # LLM call
        resp = llm_model.generate([{"role": "user", "content": prompt}])
        try:
            text = resp.generations[0][0].text.strip()
        except Exception:
            text = str(resp).strip()

        return {
            "answer": text
        }

# Escalation Agent
class EscalationSupervisor:
    def __init__(self, conversation_history: List[Dict[str, str]]):
        self.conversation_history = conversation_history

    def answer(self,conversation_history: List[dict]) -> Dict[str, str]:
        print("Escalation: Waiting for human agent response...")

        # Capture the length BEFORE waiting
        initial_len = len(self.conversation_history)

        for _ in range(20):
            # If conversation list grows → possibly new message
            if len(self.conversation_history) > initial_len:
                last_msg = self.conversation_history[-1]
                if last_msg.get("role") == "agent":
                    print("Human agent responded!")
                    return {
                        "answer": last_msg["text"]
                    }
            time.sleep(1)
        Ticketer = TicketingAgent(conversation_history)
        result = Ticketer.create_ticket(conversation_history)
        return {"answer":f"Raising Ticket for You {result}"}

# Ticketing Agent
class TicketingAgent:
    def __init__(self,conversation_history):
        self.conversation_history=conversation_history

    def llm_summarize(self, text_list: List[str], kind: str) -> str:
        if not text_list:
            return ""
        combined = " ".join(text_list)

        prompt = f"""
        Rewrite the following {kind} description into ONE clean, short sentence:
        "{combined}"

        The sentence should be formal, clear, and concise.
        """

        try:
            # Gemini LLM call (correct way)
            result = llm_model.invoke(prompt)

            # result is a string for ChatGoogleGenerativeAI
            summary = result.strip()
            return summary

        except Exception:
            # fallback
            return combined[:300] + ("..." if len(combined) > 300 else "")

    def create_ticket(self, conversation_history: List[Dict[str, str]]):
        init_db()
        user_msgs = [turn["text"] for turn in conversation_history if turn["role"] == "user"]
        agent_msgs = [turn["text"] for turn in conversation_history if turn["role"] == "agent"]

        # generate summaries (LLM-powered)
        problem_summary = self.llm_summarize(user_msgs, "problem")
        solution_summary = self.llm_summarize(agent_msgs, "solution")

        # generate ticket id
        ticket_id = "T-" + uuid.uuid4().hex[:8]

        # save into SQLite
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tickets (ticket_id, problem_summary, solution_summary) VALUES (?, ?, ?)",
            (ticket_id, problem_summary, solution_summary),
        )
        conn.commit()
        conn.close()

        return {
            "answer": f"Ticket : {ticket_id} has been created for you"
        }