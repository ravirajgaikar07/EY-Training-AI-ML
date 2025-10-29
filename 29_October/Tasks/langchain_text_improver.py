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
    temperature=0.4,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url,
)

def improve_writing(user_text: str) -> str:
    prompt = (
        "You are a professional writing assistant. "
        "Analyze the text, briefly describe its issues, "
        "and then suggest a clearer, more professional rewrite.\n\n"
        f"Text: {user_text}"
    )
    response = llm.invoke(prompt)
    return response.content.strip()

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    if user_input.lower().startswith("improve "):
        user_text = user_input[8:].strip()
        if not user_text:
            print("Agent: Please provide text to improve.")
            continue

        improved = improve_writing(user_text)
        print(f"Agent: {improved}")

        memory.save_context({"input": user_text}, {"output": improved})
        continue

    try:
        response = llm.invoke(user_input)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)
