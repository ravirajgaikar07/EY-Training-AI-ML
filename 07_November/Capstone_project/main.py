import requests
from fastapi import FastAPI, HTTPException
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")
class Query(BaseModel):
    topic: str
    question: str


@app.post("/ask")
async def generate_response(query : Query):
    try:
        prompt = "You have deep knowledge about " + query.topic + " so answer the following question " + query.question
        body={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Knowledge Assistant"
        }
        response=requests.post(url=base_url,json=body,headers=headers)
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))