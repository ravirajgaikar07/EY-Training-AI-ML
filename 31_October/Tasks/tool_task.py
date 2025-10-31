# ============================================================
# Memory-Tools.py — Conversational Mistral Agent (fully working)
# ============================================================

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import requests

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
weather_api_key = os.getenv("WEATHER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    max_tokens=256,
    api_key=api_key,
    base_url=base_url,
)

def weather(city: str) -> str:
    url_1 = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={weather_api_key}"
    response_1 = requests.get(url_1)
    lat=None
    lon=None
    if response_1.status_code == 200:
        data_1 = response_1.json()
        first_city = data_1[0]
        lat = first_city["lat"]
        lon = first_city["lon"]
    else:
        print(f"Error: {response.status_code}")
    temperature = "Not Known"
    if lat is not None and lon is not None:
        url_2=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}"
        response_2 = requests.get(url_2)
        if response_2.status_code == 200:
            data_2 = response_2.json()
            temperature=data_2["main"]["temp"]
        else:
            print(f"Error: {response.status_code}")
    return f"The temperature of {city.title()} is {temperature}."

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

print("\n=== Start chatting with your Agent ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("\nConversation ended.")
        break

    if "what" in user_input.lower() and "temperature" in user_input.lower():
        try :
            city = user_input.split("in")[-1].strip()
            if not city:
                print("Agent: Please specify a city name. Example: dubai")
            city_weather = weather(city)
            print(city_weather)
            memory.save_context({"input": user_input}, {"output": city_weather})
            continue
        except Exception as e:
            print("Agent: Could not find the temperature:", e)
            continue
    # Default: use LLM
    try:
        response = llm.invoke(user_input)
        print("Agent:", response.content)
        memory.save_context({"input": user_input}, {"output": response.content})
    except Exception as e:
        print("Error:", e)