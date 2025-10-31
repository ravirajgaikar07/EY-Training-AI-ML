import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from crewai import LLM
import requests

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
openweather_api_key = os.getenv("WEATHER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")
if not openweather_api_key:
    raise ValueError("WEATHER_API_KEY not found in .env file")

llm = LLM(
    model="openrouter/mistralai/mistral-7b-instruct",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=256,
)

@tool("fetch_weather")
def fetch_weather(city: str) -> str:
    """Fetches current weather data for a given city using the OpenWeather API."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return (
            f"City: {data['name']}\n"
            f"Temperature: {data['main']['temp']}°C\n"
            f"Feels Like: {data['main']['feels_like']}°C\n"
            f"Weather: {data['weather'][0]['description'].capitalize()}\n"
        )
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

weather_agent = Agent(
    role="Weather Analyst",
    goal="Fetch and summarize current weather for a given city.",
    backstory="An expert meteorologist who provides accurate and concise weather updates.",
    tools=[fetch_weather],
    llm=llm,
)

summary_agent = Agent(
    role="Weather Summarizer",
    goal="Generate a short, friendly weather summary based on the fetched data.",
    backstory="A content writer who creates concise, user-friendly weather summaries for audiences.",
    llm=llm,
)

city = input("Enter the city name: ") or 'Mumbai'

task1 = Task(
    description=f"Use the fetch_weather tool to get the latest weather report for {city}.",
    expected_output=f"Accurate weather data for {city}.",
    agent=weather_agent,
)

task2 = Task(
    description=f"Write a short, friendly weather update for {city} based on the fetched data.",
    expected_output=f"A concise, engaging summary about the weather in {city}.",
    agent=summary_agent,
)

crew = Crew(
    agents=[weather_agent, summary_agent],
    tasks=[task1, task2],
    process=Process.sequential,
)

result = crew.kickoff(inputs={"city": city})
print("\nFinal Output:\n", result)
