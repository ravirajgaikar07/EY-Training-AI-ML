import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(page_title="LangGraph Assistant", page_icon="🤖", layout="centered")

st.title("🤖 LangGraph Assistant")
st.write("Type a question below and get an intelligent response.")

query = st.text_area("Your question:", placeholder="Ask something like 'add 5 and 7' or 'reverse hello'")
if st.button("Submit"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": query})
                if response.status_code == 200:
                    st.success("Response:")
                    st.write(response.json()["response"])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
