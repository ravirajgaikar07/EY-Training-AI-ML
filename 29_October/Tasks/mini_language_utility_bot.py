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
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def count_words(user_text):
    words=user_text.split()
    return len(words)

def reverse_sentence(user_text):
    words = user_text.split(' ')
    reversed_words = words[::-1]
    return ' '.join(reversed_words)

def define_word(user_text):
    prompt = (
        "You are an expert in defining things"
        f"Provide an one line definition for {user_text}"
    )
    response = llm.invoke(prompt)
    return response

def repeat_word(user_text):
    parts=user_text.split(' ')
    times=int(parts[1])
    sentence=(parts[0] + ' ')* times
    return sentence.strip()

def print_history():
    data = memory.load_memory_variables({})
    chat_history = data["chat_history"]

    print("\n=== Conversation History ===")
    for msg in chat_history:
        role = "User" if msg.type == "human" else "Agent"
        print(f"{role}: {msg.content}")


print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    #Tool 1
    if user_input.lower().startswith("count "):
        user_text = user_input[6:].strip()
        if not user_text:
            print("Agent: Please provide sentence to count. ")
            continue
        count = count_words(user_text)
        print(f'Agent: Your sentence has {count} words.')

        memory.save_context({"input": user_input.strip().lower()}, {"output": f"{count} words"})
        continue

    #Tool 2
    if user_input.lower().startswith("reverse "):
        user_text = user_input[8:].strip()
        if not user_text:
            print("Agent: Please provide sentence to reverse. ")
            continue
        output_sentence = reverse_sentence(user_text)
        print(f'Agent: {output_sentence}')

        memory.save_context({"input": user_input.strip().lower()}, {"output": output_sentence})
        continue

    #Tool 3
    if user_input.lower().startswith("define "):
        user_text = user_input[7:].strip()
        if not user_text:
            print("Agent: Please provide word to define. ")
            continue
        definition = define_word(user_text)
        print(f'Agent: {definition}')

        memory.save_context({"input": user_input.strip().lower()}, {"output":definition})
        continue

    #Tool 4
    if user_input.lower().startswith("upper ") or user_input.lower().startswith("lower ") :
        if user_input.lower().startswith("upper "):
            user_text = user_input[6:].strip()
            if not user_text:
                print("Agent: Please provide sentence to upper. ")
                continue
            output_sentence = user_text.upper()
            print(f'Agent: {output_sentence}')
            memory.save_context({"input": user_input.strip().lower()}, {"output": output_sentence})
            continue
        if user_input.lower().startswith("lower "):
            user_text = user_input[6:].strip()
            if not user_text:
                print("Agent: Please provide sentence to lower. ")
                continue
            output_sentence = user_text.lower()
            print(f'Agent: {output_sentence}')
            memory.save_context({"input": user_input.strip().lower()}, {"output": output_sentence})
            continue
        print("Agent: Command not recognised try again")
        continue

    #Tool 5
    if user_input.lower().startswith("repeat "):
        user_text = user_input[7:].strip()
        if not user_text:
            print("Agent: Please provide word to repeat. ")
            continue
        words = repeat_word(user_text)
        print(f'Agent: {words}')

        memory.save_context({"input": user_input.strip().lower()}, {"output": words})
        continue

    #Bonus Tool
    if user_input.lower().startswith("history "):
        print_history()
        continue

    #default
    try:
        response = llm.invoke(user_input)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)
