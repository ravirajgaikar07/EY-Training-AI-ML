import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # You can switch to gpt-4 or mistral
    api_key=api_key,
    base_url=base_url,
    temperature=0.4
)

# Research Agent
def research_agent(topic: str) -> str:
    """Fetch research info using LLM."""
    prompt = f"Research the latest information about {topic}. Provide 5 key points with sources, dates, and relevant context."
    response = llm.invoke(prompt)  # Synchronous call
    return response.content.strip() if response.content else "No research result."

# Summarizer Agent
def summarizer_agent(research_text: str) -> str:
    """Summarize the research result."""
    if not research_text.strip():
        return "No valid research data was returned."
    prompt = f"Summarize the following research into 3 concise bullet points:\n\n{research_text}"
    response = llm.invoke(prompt)
    return response.content.strip() if response.content else "No summary generated."

# Notifier Agent
def notifier_agent(summary: str, save_to_file: bool = False):
    """Print or save the summary."""
    if save_to_file:
        with open("final_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        print("✅ Summary saved to final_summary.txt")
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




































# import os
# import asyncio
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
#
# # Load environment variables
# load_dotenv()
# api_key = os.getenv("OPENROUTER_API_KEY")
# base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
#
# # Initialize LLM
# llm = ChatOpenAI(
#     model="gpt-3.5-turbo",  # You can switch to gpt-4 or mistral
#     api_key=api_key,
#     base_url=base_url,
#     temperature=0.4
# )
#
# # Research Agent (async)
# async def research_agent(topic: str) -> str:
#     """Fetch research info using LLM."""
#     prompt = f"Research the latest information about {topic}. Provide 5 key points with sources, dates, and relevant context."
#     response = await llm.ainvoke(prompt)  # Correct async method
#     return response.content.strip() if response.content else "No research result."
#
# # Summarizer Agent (async)
# async def summarizer_agent(research_text: str) -> str:
#     """Summarize the research result."""
#     if not research_text.strip():
#         return "No valid research data was returned."
#     prompt = f"Summarize the following research into 3 concise bullet points:\n\n{research_text}"
#     response = await llm.ainvoke(prompt)
#     return response.content.strip() if response.content else "No summary generated."
#
# # Notifier Agent
# def notifier_agent(summary: str, save_to_file: bool = False):
#     """Print or save the summary."""
#     if save_to_file:
#         with open("final_summary.txt", "w", encoding="utf-8") as f:
#             f.write(summary)
#         print("✅ Summary saved to final_summary.txt")
#     else:
#         print("\n===== FINAL SUMMARY =====")
#         print(summary)
#         print("=========================")
#
# # Main function (async)
# async def main():
#     topic = input("🔍 Enter a topic to research: ")
#
#     print("\n[1] Researching...")
#     research_output = await research_agent(topic)
#
#     print("\n[2] Summarizing...")
#     summary_output = await summarizer_agent(research_output)
#
#     print("\n[3] Notifying...")
#     notifier_agent(summary_output, save_to_file=True)
#
# # Run the main function
# if __name__ == "__main__":
#     asyncio.run(main())