import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage

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

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def sentiment_analyzer(user_text: str) -> str:
    messages = [
        SystemMessage(content="You are a concise sentiment analyzer."),
        HumanMessage(content=f"Detect emotional tone in user text as positive, neutral or negative.\n\n{user_text}")
    ]
    response = llm.invoke(messages)
    return response.content

print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    if "analyze" in user_input.lower():
        try:
            parts = user_input.lower().split("analyze", 1)
            user_text = parts[1].strip() if len(parts) > 1 else ""
            if not user_text:
                print("Agent: Please provide text to analyze.")
                continue

            answer = sentiment_analyzer(user_text)
            print("Agent: The sentiment is ", answer)
            memory.save_context({"input": user_text}, {"output": answer})
            continue

        except Exception as e:
            print("Agent: Could not analyze:", e)
            continue

    try:
        response = llm.invoke(user_input)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)