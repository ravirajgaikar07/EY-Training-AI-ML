import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY missing in .env")

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.7,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url,
)
prompt = ChatPromptTemplate.from_template(
    "<s>[INST] You are a helpful assistant. Answer the following {question}. Consider the following conversation history for context: {history} [/INST]"
)

parser = StrOutputParser()

def generate_answer(question, history):
    chain = prompt | llm | parser
    history_text = "\n".join([f"User: {h[0]}\nAI: {h[1]}" for h in history])
    response = chain.invoke({"question":question, "history":history_text})
    return response
history = []
print("---Start Chatting With Memory---")
print("Hello, I am here to help you, go ahead and ask questions")
while(True):
  user_question = input("You : ").strip()
  if user_question == "exit":
    print("Ending the Chat....")
    break
  response = generate_answer(user_question, history)
  history.append((user_question,response))
  print(f"AI : {response}")