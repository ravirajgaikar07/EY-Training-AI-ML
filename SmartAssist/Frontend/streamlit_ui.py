import streamlit as st
import requests
from pathlib import Path

# ---------------------------
# Config
# ---------------------------
API_URL = "http://127.0.0.1:8000"  # Change if your FastAPI runs elsewhere

st.set_page_config(page_title="AI Support Agent", layout="wide")
st.title("Agentic AI Testing UI")

# ---------------------------
# Upload Section
# ---------------------------
st.header("Upload Documents")

uploaded_files = st.file_uploader(
    "Upload FAQ PDFs or Manual TXTs",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if st.button("Upload Files") and uploaded_files:
    files_to_send = []
    for f in uploaded_files:
        files_to_send.append(("files", (f.name, f, f.type)))

    with st.spinner("Uploading files..."):
        response = requests.post(f"{API_URL}/upload_docs", files=files_to_send)

    if response.status_code == 200:
        st.success("Files uploaded successfully!")
        for item in response.json().get("files_processed", []):
            st.write(item)
    else:
        st.error(f"Error uploading files: {response.text}")

# ---------------------------
# Query Section
# ---------------------------
st.header("Ask a Question / Troubleshooting")
query_input = st.text_input("Enter your question here:")

if st.button("Send Query") and query_input:
    with st.spinner("Getting response..."):
        response = requests.post(f"{API_URL}/query", json={"query": query_input})

    if response.status_code == 200:
        data = response.json()
        st.subheader("AI Response")
        st.write(data.get("answer", ""))

        st.subheader("Conversation History")
        history = data.get("conversation_history", [])
        for turn in history:
            role = turn.get("role", "")
            text = turn.get("text", "")
            st.markdown(f"**{role.capitalize()}:** {text}")
    else:
        st.error(f"Error: {response.text}")

# ---------------------------
# Escalation Check
# ---------------------------
st.header("Escalation Status")

if st.button("Check Escalation"):
    response = requests.get(f"{API_URL}/check")
    if response.status_code == 200:
        data = response.json()
        st.write(data)
    else:
        st.error(f"Error: {response.text}")
