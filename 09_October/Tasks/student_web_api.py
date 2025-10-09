from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

students = [
    {"id": 1, "name": "Rahul"},
    {"id": 2, "name": "Neha"},
    {"id": 3, "name": "Vivek"},
    {"id": 4, "name": "Disha"},
    {"id": 5, "name": "John"},
]

@app.get("/students")
def get_students():
    return students