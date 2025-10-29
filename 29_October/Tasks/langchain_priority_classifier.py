import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct:free",
    temperature=0.3,
    max_tokens=64,
    api_key=api_key,
    base_url=base_url,
)

def categorize_priority(user_text: str) -> str:
    text_lower = user_text.lower()

    high_keywords = ["urgent", "today", "tonight", "immediately", "asap", "deadline", "submit"]
    medium_keywords = ["soon", "next week", "important", "review", "prepare"]
    low_keywords = ["buy", "remind", "check", "call", "clean", "snacks"]

    if any(k in text_lower for k in high_keywords):
        return "HIGH"
    elif any(k in text_lower for k in medium_keywords):
        return "MEDIUM"
    elif any(k in text_lower for k in low_keywords):
        return "LOW"

    prompt = (
        "Classify the following task as HIGH, MEDIUM, or LOW priority. "
        "Only return one of those three words.\n\n"
        f"Task: {user_text}"
    )
    response = llm.invoke(prompt)
    result = response.content.strip().upper()

    if "HIGH" in result:
        return "HIGH"
    elif "MEDIUM" in result:
        return "MEDIUM"
    elif "LOW" in result:
        return "LOW"
    else:
        return "MEDIUM"

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    if user_input.lower().startswith("priority "):
        task_text = user_input[9:].strip()
        if not task_text:
            print("Agent: Please provide a task to categorize.")
            continue

        priority = categorize_priority(task_text)
        print(f'Agent: Task "{task_text}" marked as {priority} priority.')

        memory.save_context({"input": task_text}, {"output": priority})
        continue

    try:
        response = llm.invoke(user_input)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)
