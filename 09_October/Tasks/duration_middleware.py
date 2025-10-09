from fastapi import FastAPI, Request
import logging
import time
import traceback

app = FastAPI()
# ---------------- SETUP STRUCTURED LOGGING ----------------
logging.basicConfig(
    filename="app_time.log",
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

# ---------------- REQUEST LOGGING MIDDLEWARE ----------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        duration = round(time.time() - start, 3)
        logging.error(
            f"Exception in {request.method} {request.url.path}: {str(e)}\n{traceback.format_exc()}"
        )
        raise e
    duration = round(time.time() - start, 3)
    response.headers["Time_Taken"] = str(duration)
    logging.info(
        f"{request.method} {request.url.path} | Status: {response.status_code} | Duration: {duration}s"
    )
    return response

# ---------------- ROUTES ----------------
students = [{"id": 1, "name": "Rahul"}, {"id": 2, "name": "Neha"}]

@app.get("/students")
def get_students():
    logging.info("Fetching all students from database...")
    time.sleep(10)
    return students