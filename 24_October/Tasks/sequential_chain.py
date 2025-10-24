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

summary_prompt = ChatPromptTemplate.from_template(
    "<s>[INST] You are a concise assistant. Explain {topic} in simple terms for a beginner. [/INST]"
)
quiz_prompt = ChatPromptTemplate.from_template(
    "<s>[INST] Based on the {summary} generate 3 quiz questions. [/INST]"
)

parser = StrOutputParser()

def generate_summary(topic):
    summary_chain = summary_prompt | llm | parser
    response = summary_chain.invoke({"topic":topic})
    return response

def generate_quiz(summary):
    quiz_chain = quiz_prompt | llm | parser
    response = quiz_chain.invoke({"summary":summary})
    return response

user_topic = input("Enter a topic to summarize and generate quiz: ").strip()
summary = generate_summary(user_topic)
quiz = generate_quiz(summary)

print("\n---SUMMARY---")
print(summary)

print("\n---QUIZ QUESTIONS---")
print(quiz)

os.makedirs("logs",exist_ok=True)
log_entry = {
    "timestamp":datetime.utcnow().isoformat(),
    "topic":user_topic,
    "summary":summary,
    "quiz":quiz
}

with open("logs/prompt_template_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry) + "\n")

print("\nResponse logged to logs/prompt_template_log.jsonl")