# chat_ui.py
import streamlit as st
from backend import process_prompt

st.title("📧 Email Bot (Ollama + MCP)")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Write your message...")

# When user hits Send
if st.button("Send") and user_input:

    # Add user's message
    st.session_state.history.append(("user", user_input))

    # Process reply
    reply = process_prompt(user_input)

    # Add assistant's reply to history
    st.session_state.history.append(("assistant", reply))


for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)
