from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import asyncio

load_dotenv()

app = FastAPI()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url,
)

class Prompt(BaseModel):
    query: str

history_path = Path("qa_history.jsonl")
file_lock = asyncio.Lock()

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Chat Assistant</title>
        <style>
            body {
                margin: 0;
                font-family: 'Inter', sans-serif;
                background-color: #0e1117;
                color: #e4e6eb;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            header {
                background-color: #1b1f27;
                padding: 1rem;
                text-align: center;
                font-size: 1.4rem;
                font-weight: 600;
                color: #58a6ff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            #chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                padding: 1rem;
                overflow-y: auto;
                scroll-behavior: smooth;
            }
            .message {
                max-width: 70%;
                margin-bottom: 0.8rem;
                padding: 0.8rem 1rem;
                border-radius: 12px;
                line-height: 1.5;
                animation: fadeIn 0.3s ease-in-out;
            }
            .user {
                background-color: #238636;
                align-self: flex-end;
            }
            .bot {
                background-color: #30363d;
                align-self: flex-start;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            #input-container {
                display: flex;
                background-color: #161b22;
                padding: 0.8rem;
                border-top: 1px solid #30363d;
            }
            #query {
                flex: 1;
                padding: 0.6rem 0.8rem;
                background-color: #0d1117;
                border: 1px solid #30363d;
                color: #e4e6eb;
                border-radius: 8px;
                font-size: 1rem;
                outline: none;
            }
            button {
                margin-left: 0.6rem;
                background-color: #238636;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1.2rem;
                font-size: 1rem;
                cursor: pointer;
                transition: background 0.2s;
            }
            button:hover {
                background-color: #2ea043;
            }
        </style>
    </head>
    <body>
        <header>🤖 AI Chat Assistant</header>
        <div id="chat-container"></div>
        <div id="input-container">
            <input type="text" id="query" placeholder="Type your question..." />
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            const chatContainer = document.getElementById("chat-container");
            const queryInput = document.getElementById("query");

            function appendMessage(sender, text) {
                const msg = document.createElement("div");
                msg.classList.add("message", sender);
                msg.textContent = text;
                chatContainer.appendChild(msg);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function sendMessage() {
                const query = queryInput.value.trim();
                if (!query) return;
                appendMessage("user", query);
                queryInput.value = "";

                appendMessage("bot", "⏳ Thinking...");

                const response = await fetch("/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query })
                });

                const data = await response.json();
                const lastBotMsg = chatContainer.querySelector(".bot:last-child");
                if (response.ok && data.response) {
                    lastBotMsg.textContent = data.response;
                } else {
                    lastBotMsg.textContent = "⚠️ Error: " + (data.detail || data.error || "Unknown error");
                }
            }

            queryInput.addEventListener("keypress", (e) => {
                if (e.key === "Enter") sendMessage();
            });
        </script>
    </body>
    </html>
    """

@app.post("/generate")
async def generate_response(prompt: Prompt):
    if not prompt.query.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty")
    try:
        response = llm.invoke([
            SystemMessage(content="You are a helpful assistant who provides clear and accurate responses."),
            HumanMessage(content=prompt.query)
        ])
        new_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": prompt.query,
            "response": response.content
        }
        async with file_lock:
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(new_log, ensure_ascii=False) + "\n")

        return {"response": response.content}

    except Exception as e:
        new_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": prompt.query,
            "error": str(e)
        }
        async with file_lock:
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(new_log, ensure_ascii=False) + "\n")
        raise HTTPException(status_code=500, detail=str(e))
