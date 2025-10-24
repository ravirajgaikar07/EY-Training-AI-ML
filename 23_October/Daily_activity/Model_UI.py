import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 1. Load environment variables from .env
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# 2. Initialize LangChain model pointing to OpenRouter
llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.7,
    max_tokens=500,
    api_key=api_key,
    base_url=base_url
)


# 3. Function to get the model's response
def get_model_response(user_input):
    # Define messages (Mistral models work better with [INST]...[/INST])
    messages = [
        SystemMessage(content="You are a helpful and concise AI assistant."),
        HumanMessage(content=f"<s>[INST] {user_input} [/INST]"),
    ]

    try:
        response = llm.invoke(messages)
        return response.content.strip() or "(no content returned)"
    except Exception as e:
        return f"Error: {str(e)}"


# Streamlit UI
st.set_page_config(page_title="AI Assistant", page_icon="✔", layout="wide")
st.title("Your AI Assistant")

st.markdown("## Enter a question below and get an answer:")

# User input for the question
user_input = st.text_area("Your Question", height=150, placeholder="Ask about any topic...")

# Submit button to get the response
if st.button("Get Answer"):
    if user_input.strip() != "":
        with st.spinner("Thinking..."):
            response = get_model_response(user_input)
        st.markdown("### Assistant's Response:")
        st.write(response)
    else:
        st.warning("Please enter a question.")
