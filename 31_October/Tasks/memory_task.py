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
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url,
)


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    try:
        memory_context = memory.load_memory_variables({}).get("chat_history", [])
        context_str = "\n".join(
            [f"User: {msg.content}" if msg.type=='human' else f"Agent: {msg.content}" for msg in memory_context]
        )
        prompt = (
            f"You are a helpful assistant. Answer the question: '{user_input}'. "
            f"Here is the context:\n{context_str}"
        )
        response = llm.invoke(prompt)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)