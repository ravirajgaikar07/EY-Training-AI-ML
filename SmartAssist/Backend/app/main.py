from fastapi import FastAPI, UploadFile, File, Form, Request,HTTPException
from typing import List
from .ingest import ingest_and_store_embeddings_Manual, ingest_and_store_embeddings_FAQ
from .graph import run_workflow
from .schemas import QueryResponse, UploadResponse
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
app = FastAPI()
state = {"is_escalation": False}
@app.post("/upload_docs", response_model=UploadResponse)
async def upload_docs(files: List[UploadFile] = File(...)):
    faq_files = []
    manual_files = []

    # Classify files based on extension
    for file in files:
        if file.filename.lower().endswith(".pdf"):
            faq_files.append(file)
        elif file.filename.lower().endswith(".txt"):
            manual_files.append(file)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )

    processed = []

    # Process FAQ PDFs → FAQ FAISS index
    if faq_files:
        await ingest_and_store_embeddings_FAQ(faq_files)
        processed.append(f"Ingested {len(faq_files)} FAQ PDFs")

    # Process Manuals TXT → Manual FAISS index
    if manual_files:
        await ingest_and_store_embeddings_Manual(manual_files)
        processed.append(f"Ingested {len(manual_files)} Manual TXTs")

    return UploadResponse(
        success=True,
        message="Files processed successfully",
        files_processed=processed
    )

conversation_history: List[dict] = []
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req):
    conversation_history.append({"role": "user", "text": req.query})
    res = await run_workflow(conversation_history)
    conversation_history.append({"role": "agent", "text": res["answer"]})
    return QueryResponse(
        answer=res["answer"],
        conversation_history=conversation_history
    )
@app.post("/human/reply")
def human_reply(reply: str):
    if not conversation_history:
        return {"error": "invalid convo"}
    conversation_history.append({"role": "agent", "text": reply})
    return {"history": "conversation_history"}

@app.get("/check")
def any_changes():
    if state["is_escalation"]:
        return {"status": "True",
                "history": conversation_history}
    return {"status": "False"}



