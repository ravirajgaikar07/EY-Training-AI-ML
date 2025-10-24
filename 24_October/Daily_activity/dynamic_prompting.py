import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ----------------------------------------------------------
# 1. Load environment variables
# ----------------------------------------------------------
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY missing in .env")

# ----------------------------------------------------------
# 2. Initialize model (Mistral via OpenRouter)
# ----------------------------------------------------------
llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.7,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url,
)

# ----------------------------------------------------------
# 3. Define a dynamic ChatPromptTemplate
# ----------------------------------------------------------
prompt = ChatPromptTemplate.from_template(
    "<s>[INST] You are a concise assistant. Explain {topic} in simple terms for a beginner. [/INST]"
)

parser = StrOutputParser()

def generate_explanation(topic):
    chain = prompt | llm | parser
    response = chain.invoke({"topic":topic})
    return response

user_topic = input("Enter a topic you want explained: ").strip()
response = generate_explanation(user_topic)

print("\n Mistral Response")

os.makedirs("logs",exist_ok=True)
log_entry = {
    "timestamp":datetime.utcnow().isoformat(),
    "topic":user_topic,
    "response":response
}

with open("logs/prompt_template_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry) + "\n")

print("\nResponse logged to logs/prompt_template_log.jsonl")
