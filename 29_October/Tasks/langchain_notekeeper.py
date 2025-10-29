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

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
notes_memory = ConversationBufferMemory(memory_key="notes", return_messages=True)

print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    if user_input.lower().startswith("note "):
        note_text = user_input[5:].strip()
        if not note_text:
            print("Agent: Please provide a note to remember.")
            continue
        notes_memory.save_context({"input": "note"}, {"output": note_text})
        print(f'Agent: Noted: "{note_text}"')
        continue

    if user_input.lower() == "get notes":
        notes = [
            msg.content for msg in notes_memory.load_memory_variables({})["notes"]
            if msg.type == "ai"
        ]
        if not notes:
            print("Agent: You currently have no notes.")
        else:
            formatted_notes = "; ".join([f'"{n}"' for n in notes])
            print(f"Agent: You currently have {len(notes)} note(s): {formatted_notes}")
        continue

    try:
        response = llm.invoke(user_input)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)
