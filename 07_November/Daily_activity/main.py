from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # load OPENAI_API_KEY

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Prompt(BaseModel):
    query: str

@app.post("/generate")
async def generate_response(prompt: Prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # or "gpt-4-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt.query}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}