# mcp_client.py
import json
import requests
import ollama      # <-- official Python library

MODEL = "llama3.1:8b"
MCP = "http://localhost:5001"


# -----------------------------------------------------
# Call Ollama exactly like your Streamlit app does
# -----------------------------------------------------
def call_llm(prompt):
    """
    Calls local Ollama using the official python client.
    Converts user instruction → JSON only.
    """
    system_prompt = (
        "You ONLY output valid JSON.\n"
        "No explanations.\n"
        "No natural language.\n"
        "No extra text.\n"
        "Just return exactly this structure:\n"
        "{ \"to\": \"email@example.com\", \"subject\": \"subject text\", \"body\": \"email body\" }"
    )

    user_prompt = (
        f"Convert the following instruction into JSON only.\n"
        f"User instruction:\n"
        f"{prompt}\n\n"
        "Return ONLY valid JSON."
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        print("❌ Error calling Ollama:", e)
        return None


# -----------------------------------------------------
# Parse JSON returned by Ollama
# -----------------------------------------------------
def parse_llm_response(raw_content):
    """
    The LLM ALWAYS returns JSON like:
       { "to": "...", "subject": "...", "body": "..." }
    Extract and return as Python dict.
    """

    try:
        data = json.loads(raw_content)
        return data
    except Exception as e:
        print("❌ Invalid JSON from LLM:", raw_content)
        print("Error:", e)
        return None


# -----------------------------------------------------
# Call MCP Server tool
# -----------------------------------------------------
def call_mcp(email_data):
    """
    email_data = {
        "to": "...",
        "subject": "...",
        "body": "..."
    }
    """

    payload = {
        "name": "send_email",
        "args": {
            "to": email_data["to"],
            "subject": email_data["subject"],
            "body": email_data["body"]
        }
    }

    resp = requests.post(f"{MCP}/call", json=payload, timeout=20)
    resp.raise_for_status()

    return resp.json()


# -----------------------------------------------------
# Main function: UI → LLM → MCP
# -----------------------------------------------------
def run_once(prompt):

    # 1) Ask Ollama (as you do in Streamlit)
    raw_json = call_llm(prompt)
    print("\n=== Raw LLM Output ===")
    print(raw_json)

    if not raw_json:
        return {"type": "error", "message": "LLM returned nothing"}

    # 2) Parse JSON returned by LLM
    email_data = parse_llm_response(raw_json)
    if not email_data:
        return {"type": "error", "message": "LLM JSON parsing failed"}

    print("\n=== Parsed Email JSON ===")
    print(email_data)

    # 3) Call MCP Server tool
    result = call_mcp(email_data)

    return {
        "type": "tool_result",
        "tool": "send_email",
        "result": result
    }
