from fastapi import FastAPI, Request
import logging
import time
import traceback

app = FastAPI()
app.state.request_count = 0
# ---------------- SETUP STRUCTURED LOGGING ----------------
logging.basicConfig(
    filename="app.log",
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

# ---------------- REQUEST LOGGING MIDDLEWARE ----------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    app.state.request_count += 1
    logging.info(f"No. of visits to website: {app.state.request_count}")
    try:
        response = await call_next(request)
    except Exception as e:
        duration = round(time.time() - start, 3)
        logging.error(
            f"Exception in {request.method} {request.url.path}: {str(e)}\n{traceback.format_exc()}"
        )
        raise e
    duration = round(time.time() - start, 3)
    logging.info(
        f"{request.method} {request.url.path} | Status: {response.status_code} | Duration: {duration}s"
    )
    return response

# ---------------- ROUTES ----------------
students = [{"id": 1, "name": "Rahul"}, {"id": 2, "name": "Neha"}]

@app.get("/students")
def get_students():
    logging.info("Fetching all students from database...")
    return students