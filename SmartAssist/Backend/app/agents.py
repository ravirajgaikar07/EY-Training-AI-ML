import os
import time
import uuid
import faiss
import sqlite3
import numpy as np
from typing import List, Dict
from .db import init_db
from langchain_google_genai import GoogleGenerativeAI
from .ingest import FAQ_METADATA, MANUAL_METADATA, embedding_model
from .logger import logger
import asyncio


# ---------------------------
# Global LLM and Index Setup
# ---------------------------
llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")
FAQ_INDEX_PATH = "faiss_indexes/faq.index"
MANUAL_INDEX_PATH = "faiss_indexes/manual.index"
DB_PATH = "tickets.db"
DIM = 768

def load_or_create_index(path, dim):
    if os.path.exists(path):
        logger.info("Loading FAISS index from %s", path)
        return faiss.read_index(path)
    logger.info("Creating new FAISS index at %s", path)
    return faiss.IndexFlatL2(dim)

FAQ_INDEX = load_or_create_index(FAQ_INDEX_PATH, DIM)
MANUAL_INDEX = load_or_create_index(MANUAL_INDEX_PATH, DIM)

# ---------------------------
# Intent Classifier
# ---------------------------
class IntentRouter:
    def __init__(self):
        pass

    def answer(self, query: str, history: str) -> str:
        prompt = f""" You are an extremely strict INTENT CLASSIFIER. You must choose EXACTLY ONE label from the following: ------------------------------------------------------------ VALID LABELS: 1. faq → general questions, how-to, product info, explanations 2. troubleshoot → errors, malfunctions, app/device not working, technical issues 3. escalation → user frustration OR unclear OR no answer possible ------------------------------------------------------------ ### Rules for Classification ### #### 1. FAQ Choose **faq** ONLY IF: - The user asks for general information - "What is…", "How does it work?", "Explain…", "Where can I find…" - No sign of errors or frustration - User is calm and asking informational questions #### 2. Troubleshoot Choose **troubleshoot** when: - User reports any error, bug, malfunction, failure - “App crashed”, “Not working”, “Error code”, “Cannot login”, “Device won't start” - There is a technical issue that needs guided diagnosis #### 3. Escalation Choose **escalation** when: - The system cannot fulfill the request - User is frustrated, angry, or repeating questions - History shows unresolved attempts - User says things like: “This is not helping”, “You already asked this”, “I want a human”, “You are useless” - The query is unclear, ambiguous, or does not match faq/troubleshoot - You are unsure → **always escalate** ------------------------------------------------------------ INPUTS PROVIDED TO YOU User Query: {query} Chat History (most recent first): {history} ------------------------------------------------------------ Return ONLY ONE word: faq, troubleshoot, or escalation. """
        try:
            llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")
            response = llm_model.generate([prompt])
            refined = response.generations[0][0].text.strip()
            logger.info("IntentClassifier output: %s", refined)
            return refined
        except Exception as e:
            logger.error("IntentRouter error: %s", str(e))
            return "escalation"

    async def route(self, conversation_history: List[dict]) -> dict:
        last_msgs = conversation_history[-10:]
        parts = [f"{'User' if m['role']=='user' else 'Agent'}: {m['text']}" for m in last_msgs]
        history = "\n".join(parts)
        last_user_msgs = [m for m in reversed(conversation_history) if m["role"] == "user"]
        query = last_user_msgs[0]["text"] if last_user_msgs else ""
        intent = self.answer(query, history)
        logger.info("Routing intent: %s", intent)
        return {"answer": intent if intent in ["faq","troubleshoot","escalation"] else "escalation"}

# ---------------------------
# RAG FAQ Agent
# ---------------------------
class RAGFAQAgent:
    def __init__(self):
        pass

    def retrieve_faq_context(self, query: str, top_k=4, min_score=0.30):
        try:
            q_emb = embedding_model.embed_query(query)
            qv = np.array([q_emb], dtype="float32")
            qv /= (np.linalg.norm(qv) + 1e-10)
            scores, ids = FAQ_INDEX.search(qv, top_k)
            results = [
                {"text": FAQ_METADATA[idx]["text"], "score": float(score)}
                for idx, score in zip(ids[0], scores[0])
                if idx >= 0 and score >= min_score
            ]
            logger.info("Retrieved %d FAQ chunks for query", len(results))
            return results
        except Exception as e:
            logger.error("RAGFAQAgent.retrieve_faq_context error: %s", str(e))
            return []

    def answer(self, history: List[dict]):
        latest_msg = [m for m in reversed(history) if m["role"] == "user"]
        query = latest_msg[0]["text"] if latest_msg else ""
        ctx = self.retrieve_faq_context(query)
        if not ctx:
            logger.info("FAQ context empty for query: %s", query)
            return {"answer": "The FAQ repository does not contain information about this query."}
        history_text = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in history])
        source_texts = [f"[chunk {i}]\n{item['text'][:700]}\n" for i, item in enumerate(ctx)]
        prompt = (
            f"You are a strict factual assistant.\nConversation History:\n{history_text}\n"
            "FAQ Sources:\n" + "\n".join(source_texts) + "\n\nQuestion: " + query
        )
        try:
            resp = llm_model.generate([prompt])
            text = resp.generations[0][0].text.strip()
            logger.info("RAGFAQAgent answer generated")
            return {"answer": text}
        except Exception as e:
            logger.error("RAGFAQAgent answer error: %s", str(e))
            return {"answer": "Error generating FAQ answer."}

# ---------------------------
# Troubleshooter Agent
# ---------------------------
class TroubleshooterAgent:
    def __init__(self):
        pass

    def retrieve_manual_context(self, query: str, top_k=4, min_score=0.30):
        try:
            q_emb = embedding_model.embed_query(query)
            qv = np.array([q_emb], dtype="float32")
            qv /= (np.linalg.norm(qv) + 1e-10)
            scores, ids = MANUAL_INDEX.search(qv, top_k)
            results = [
                {"text": MANUAL_METADATA[idx]["text"], "score": float(score)}
                for idx, score in zip(ids[0], scores[0])
                if idx >= 0 and score >= min_score
            ]
            logger.info("Retrieved %d manual chunks for query", len(results))
            return results
        except Exception as e:
            logger.error("TroubleshooterAgent.retrieve_manual_context error: %s", str(e))
            return []

    def answer(self, history: List[dict]):
        latest_user_msgs = [m for m in reversed(history) if m.get("role") == "user"]
        if not latest_user_msgs:
            logger.warning("No user message found in history")
            return {"answer": "No user message found in history.", "sources": [], "confidence": 0.0}
        query = latest_user_msgs[0]["text"]
        ctx = self.retrieve_manual_context(query)
        if not ctx:
            logger.info("Manual context empty for query: %s", query)
            return {"answer": "The manual repository does not contain information about this query."}
        history_text = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in history])
        source_texts = [f"[chunk {i}]\n{item['text'][:700]}\n" for i, item in enumerate(ctx)]
        prompt = (
            "You are a precise troubleshooting assistant. Use only manual sources.\n"
            f"Conversation History:\n{history_text}\nManual Sources:\n" + "\n".join(source_texts) + "\n\nQuestion: " + query
        )

        manual_text = "\n".join(source_texts)

        prompt = f"""
        You are an expert technical support assistant. Use only the provided manual content to generate your response.
        Your response should be:

        1. Clear and concise.
        2. Step-by-step if troubleshooting steps are available.
        3. Polite, professional, and reassuring.
        4. Avoid listing raw chunk references; instead, integrate the content into natural sentences.
        5. If the manual lacks exact information, suggest the most reasonable next steps and reassure the user.

        Conversation History:
        {history_text}

        Manual Sources:
        {manual_text}

        Question:
        {query}
        """

        try:
            resp = llm_model.generate([prompt])
            text = resp.generations[0][0].text.strip()
            logger.info("TroubleshooterAgent answer generated")
            return {"answer": text}
        except Exception as e:
            logger.error("TroubleshooterAgent answer error: %s", str(e))
            return {"answer": "Error generating troubleshooting answer."}

# ---------------------------
# Escalation Supervisor
# ---------------------------
class EscalationSupervisor:
    def __init__(self, conversation_history: List[Dict[str, str]]):
        self.conversation_history = conversation_history

    async def answer(self, conversation_history: List[dict]) -> Dict[str, str]:
        logger.info("EscalationSupervisor waiting for human agent response...")
        initial_len = len(self.conversation_history)
        for _ in range(20):
            if len(self.conversation_history) > initial_len:
                last_msg = self.conversation_history[-1]
                if last_msg.get("role") == "agent":
                    logger.info("Human agent responded")
                    return {"answer": last_msg["text"]}
            await asyncio.sleep(1)  # non-blocking
        Ticketer = TicketingAgent(conversation_history)
        result = Ticketer.create_ticket(conversation_history)
        logger.info("Ticket raised by EscalationSupervisor")
        answer=result["answer"]
        return {
            "answer": (
                f"Our team is currently reviewing your issue. "
                f"A ticket has been created: {answer['answer']}. "
                f"One of our experts will get back to you shortly. "
            )
        }


# ---------------------------
# Ticketing Agent
# ---------------------------
class TicketingAgent:
    def __init__(self, conversation_history):
        self.conversation_history = conversation_history

    def llm_summarize(self, text_list: List[str], kind: str) -> str:
        if not text_list:
            return ""
        combined = " ".join(text_list)
        prompt = f'Rewrite the following {kind} description into ONE clean, short sentence: "{combined}"'
        try:
            result = llm_model.invoke(prompt)
            summary = result.strip() if isinstance(result, str) else str(result)
            return summary
        except Exception as e:
            logger.error("TicketingAgent.llm_summarize error: %s", str(e))
            return combined[:300] + ("..." if len(combined) > 300 else "")

    def create_ticket(self, conversation_history: List[Dict[str, str]]):
        try:
            init_db()
            user_msgs = [turn["text"] for turn in conversation_history if turn["role"] == "user"]
            agent_msgs = [turn["text"] for turn in conversation_history if turn["role"] == "agent"]
            problem_summary = self.llm_summarize(user_msgs, "problem")
            solution_summary = self.llm_summarize(agent_msgs, "solution")
            ticket_id = "T-" + uuid.uuid4().hex[:8]
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tickets (ticket_id, problem_summary, solution_summary) VALUES (?, ?, ?)",
                (ticket_id, problem_summary, solution_summary),
            )
            conn.commit()
            conn.close()
            logger.info("Ticket created: %s", ticket_id)
            return {"answer": f"ticket id : {ticket_id}"}
        except Exception as e:
            logger.error("TicketingAgent.create_ticket error: %s", str(e))
            return {"answer": "Error creating ticket."}
