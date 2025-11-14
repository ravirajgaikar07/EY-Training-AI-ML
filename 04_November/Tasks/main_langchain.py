import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

# Initialize LLM
llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",  # You can switch to gpt-4 or claude for better results
    api_key=api_key,
    base_url=base_url,
    temperature=0.4,
    max_tokens=100)


# Research Agent
def research_agent(topic: str) -> str:
    prompt = f"Research the latest information about {topic}. Provide 5 key points."
    response = llm.invoke(prompt)
    print(f"DEBUG: Raw Research Response -> {response}")
    return response.content.strip() if response.content else "No research result."

# Summarizer Agent
def summarizer_agent(research_text: str) -> str:
    if not research_text.strip():
        return "No research text provided."

    # Use structured prompt
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert summarizer."),
        ("human", "Summarize the following text in 3 concise bullet points:\n\n{text}")
    ])
    prompt = template.format_messages(text=research_text[:1500])  # Truncate to avoid token overflow

    response = llm.invoke(prompt)
    print(f"DEBUG: Raw Summary Response -> {response}")
    return response.content.strip() if response.content else "⚠️ Model returned empty summary."

# Notifier Agent
def notifier_agent(summary: str, save_to_file: bool = False):
    if save_to_file:
        if summary.strip():
            with open("final_summary.txt", "w", encoding="utf-8") as f:
                f.write(summary)
            print("✅ Summary saved to final_summary.txt")
        else:
            print("⚠️ Summary is empty. Nothing written to file.")
    else:
        print("\n===== FINAL SUMMARY =====")
        print(summary)
        print("=========================")

# Main function
def main():
    topic = input("🔍 Enter a topic to research: ")

    print("\n[1] Researching...")
    research_output = research_agent(topic)

    print("\n[2] Summarizing...")
    summary_output = summarizer_agent(research_output)

    print("\n[3] Notifying...")
    notifier_agent(summary_output, save_to_file=True)

if __name__ == "__main__":
    main()