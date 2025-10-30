from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# Define LLM
llm = LLM(
    model="openrouter/mistralai/mistral-7b-instruct",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=256,
)

# Define agents
researcher = Agent(
    role="Researcher",
    goal="Find important points about the benefits of renewable energy.",
    backstory="An expert researcher who summarizes information concisely.",
    llm=llm
)

writer = Agent(
    role="Writer",
    goal="Write a short, engaging blog post about renewable energy using the researcher’s notes.",
    backstory="A creative writer skilled in turning facts into readable content.",
    llm=llm
)

# Define tasks
task1 = Task(
    description="Research and summarize 5 key benefits of renewable energy.",
    expected_output="A concise list of 5 main benefits of renewable energy.",
    agent=researcher
)

task2 = Task(
    description="Write a 200-word blog post based on the researcher's findings.",
    expected_output="A 200-word engaging blog post about renewable energy.",
    agent=writer
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    process="sequential"
)

result = crew.kickoff()
print("\nFinal Output:\n", result)
