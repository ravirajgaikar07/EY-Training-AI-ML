from autogen import AssistantAgent, UserProxyAgent
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")
client = OpenAI(api_key=api_key,base_url=base_url)

os.environ["AUTOGEN_USE_DOCKER"]='0'

assistant = AssistantAgent(
    name="Assistant",
    llm_config={"model": "mistralai/mistral-7b-instruct",
                "api_key": api_key,
                "base_url": base_url},
    code_execution_config=False
)
user_proxy = UserProxyAgent(name="UserProxy")

user_input = input("Enter your query or data: ")
response = user_proxy.initiate_chat(assistant, message=user_input)

print("\n===== AutoGen Agent Output =====")
print(response)