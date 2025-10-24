import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 1. Load environment variables from .env
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# 2. Initialize LangChain model pointing to OpenRouter
llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.7,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url
)

# 3. Define messages (Mistral models work better with [INST]...[/INST])
messages = [
    SystemMessage(content="You are a helpful and concise AI assistant."),
    HumanMessage(content="<s>[INST] Explain in simple terms how convolutional neural networks work. [/INST]"),
]

# 4. Invoke model and print response
try:
    response = llm.invoke(messages)
    print("Assistant:", response.content.strip() or "(no content returned)")
except Exception as e:
    print(e)