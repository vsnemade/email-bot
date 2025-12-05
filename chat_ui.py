import streamlit as st
import json
import ollama   # <-- IMPORTANT: use Ollama python client
import requests

OLLAMA_MODEL = "llama3.1:8b"   # your local model
MCP_SERVER_URL = "http://localhost:8000/process-email"

st.title("Email Chat Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------
# Call Ollama LLM using OFFICIAL Python client
# -----------------------------------------------------
def call_ollama(prompt):
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
           messages=[
                {
                    "role": "system",
                    "content": (
                        "You ONLY output valid JSON.\n"
                        "No explanations.\n"
                        "No natural language.\n"
                        "No extra text.\n"
                        "Just return this exact structure:\n"
                        "{ \"to\": \"email@example.com\",  \"subject\": \"subject body\", \"body\": \"email body\" }"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Convert the following instruction into JSON only.\n"
                        "User instruction:\n"
                        f"{prompt}\n\n"
                        "Return ONLY valid JSON."
                    )
                }
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error calling Ollama: {e}"


# -----------------------------------------------------
# Send email to MCP endpoint
# -----------------------------------------------------
def send_to_mcp(email_to, subject, body):
    response = requests.post(MCP_SERVER_URL, json={
        "to": email_to,
        "body": body,
        "subject": subject
    })
    return response.json()


# -----------------------------------------------------
# UI Input
# -----------------------------------------------------
user_input = st.text_input("Enter your prompt:", "")

if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "body": user_input})
    
    # LLM OUTPUT
    llm_output = call_ollama(user_input)

    # Parse JSON from LLM
    try:
        email_json = json.loads(llm_output)
        result = send_to_mcp(email_json['to'], email_json['subject'], email_json['body'])
    except json.JSONDecodeError:
        # If LLM fails to produce JSON properly
        result = {"status": "Invalid JSON", "output": llm_output}
    
    st.session_state.messages.append({"role": "assistant", "body": str(result)})

# -----------------------------------------------------
# Display messages
# -----------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['body']}")
    else:
        st.markdown(f"**Assistant:** {msg['body']}")
