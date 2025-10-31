from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

llm = LLM(
    model="openrouter/mistralai/mistral-7b-instruct",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=512
)

researcher = Agent(
    role="Researcher",
    goal="Gather detailed information and key points about the story theme provided by the user.",
    backstory="A diligent researcher who unearths crucial details for the narrative based on the input.",
    llm=llm
)

writer = Agent(
    role="Writer",
    goal="Turn the gathered research into a cohesive and engaging story based on the user's theme.",
    backstory="A creative writer who can transform facts and ideas into an immersive story.",
    llm=llm
)

def generate_story(input_theme):
    task1 = Task(
        description=f"Research the theme of '{input_theme}' and create a list of important plot points or themes for the story.",
        expected_output=f"A set of essential plot points or themes for the story about '{input_theme}'.",
        agent=researcher
    )

    task2 = Task(
        description=f"Write a compelling story about '{input_theme}' based on the researcher's findings.",
        expected_output=f"A detailed short story about '{input_theme}'.",
        agent=writer
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        process="sequential"
    )

    result = crew.kickoff()
    return result

input_theme = input("Enter the theme for your story (e.g., crow, knight, dragon, etc.): ").strip()

story_output = generate_story(input_theme)
print("\nFinal Story Output:\n", story_output)
