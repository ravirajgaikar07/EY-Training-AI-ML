import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
from .ingest import ingest_and_store_embeddings_Manual, ingest_and_store_embeddings_FAQ
from .graph import run_workflow
from .schemas import HumanRequest, QueryResponse, UploadResponse, QueryRequest
from .logger import logger
from .state import state
# ---------------------------
# Environment Setup
# ---------------------------
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Upload API
# ---------------------------
@app.post("/upload_docs", response_model=UploadResponse)
async def upload_docs(files: List[UploadFile] = File(...)):
    logger.info("Received upload_docs request with %s files", len(files))

    faq_files = []
    manual_files = []

    for file in files:
        logger.info("Processing file: %s", file.filename)

        if file.filename.lower().startswith("faq"):
            faq_files.append(file)
        elif file.filename.lower().startswith("manual"):
            manual_files.append(file)
        else:
            logger.warning("Unsupported file type attempted: %s", file.filename)
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )

    processed = []

    try:
        if faq_files:
            logger.info("Starting ingestion for FAQ PDFs: %s files", len(faq_files))
            await ingest_and_store_embeddings_FAQ(faq_files)
            processed.append(f"Ingested {len(faq_files)} FAQ PDFs")
            logger.info("Finished ingestion for FAQ PDFs")

        if manual_files:
            logger.info("Starting ingestion for Manual PDFs: %s files", len(manual_files))
            await ingest_and_store_embeddings_Manual(manual_files)
            processed.append(f"Ingested {len(manual_files)} Manual PDFs")
            logger.info("Finished ingestion for Manual PDFs")
    except Exception as e:
        logger.error("Error during ingestion: %s", str(e))
        raise HTTPException(status_code=500, detail="Ingestion failed")

    logger.info("File processing completed successfully")

    return UploadResponse(
        success=True,
        message="Files processed successfully",
        files_processed=processed
    )


# ---------------------------
# Query API
# ---------------------------
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    logger.info("Received query: %s", req.query)

    state["conversation_history"].append({"role": "user", "text": req.query})

    try:
        # RUN WORKFLOW IN BACKGROUND THREAD
        res = await run_workflow(state["conversation_history"])
    except Exception as e:
        logger.error("Workflow error: %s", str(e))
        raise HTTPException(status_code=500, detail="Workflow execution failed")

    if state["conversation_history"][-1]["role"] != "agent":
        state["conversation_history"].append({"role": "agent", "text": res["answer"]})

    logger.info("Generated response: %s", res["answer"])

    return QueryResponse(
        answer=res["answer"],
        conversation_history=state["conversation_history"]
    )


# ---------------------------
# Human Reply API
# ---------------------------
@app.post("/human/reply")
def human_reply(req: HumanRequest):
    logger.info("Human reply received: %s", req.reply)

    if not state["conversation_history"]:
        logger.warning("Human reply attempted with empty conversation history")
        return {"error": "invalid convo"}

    state["conversation_history"].append({"role": "agent", "text": req.reply})

    logger.info("Human reply added to conversation history")

    return {"history": "conversation_history"}


# ---------------------------
# Escalation Check API
# ---------------------------
@app.get("/check")
def any_changes():
    logger.info("Check endpoint hit. Escalation status: %s", state['is_escalation'])

    if state["is_escalation"]:
        return {"status": True, "history": state["conversation_history"]}

    return {"status": False}

@app.post("/reset_history")
def reset_history():
    state["conversation_history"].clear()
    state["is_escalation"] = False
    return {"status": True, "history": state["conversation_history"]}
