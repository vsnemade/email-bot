# mcp_server.py
from flask import Flask, jsonify, request
import requests
import logging

app = Flask("mcp-server")
logging.basicConfig(level=logging.INFO)

# --- Tool registry ---
TOOLS = {}

def register_tool(name, description, function, input_schema=None):
    TOOLS[name] = {
        "name": name,
        "description": description,
        "input_schema": input_schema or {},
        "function": function
    }

# --- Example tool implementation: send_email ---
def send_email_impl(args):
    """
    args expected: {"to": "...", "subject": "...", "body": "..."}
    This implementation forwards to alerts-email-service (HTTP).
    alerts-email-service runs on port 5000 and exposes /send-email
    """
    try:
        to = args["to"]
        subject = args["subject"]
        body = args["body"]
    except KeyError as e:
        return {"success": False, "error": f"missing argument {e.args[0]}"}

    try:
        resp = requests.post(
            "http://localhost:5000/send-email",
            json={"to": to, "subject": subject, "body": body},
            timeout=10
        )
        # safely parse JSON if possible
        content = None
        try:
            content = resp.json()
        except Exception:
            content = resp.text

        return {
            "success": resp.status_code == 200,
            "status_code": resp.status_code,
            "response": content
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Register the tool
register_tool(
    name="send_email",
    description="Send email via alerts-email-service (local HTTP). Args: to, subject, body",
    function=send_email_impl,
    input_schema={
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"}
        },
        "required": ["to", "subject", "body"]
    }
)

# --- API: list tools ---
@app.route("/tools", methods=["GET"])
def list_tools():
    tool_list = []
    for t in TOOLS.values():
        tool_list.append({
            "name": t["name"],
            "description": t["description"],
            "input_schema": t["input_schema"]
        })
    return jsonify({"tools": tool_list})

# --- API: call a tool ---
@app.route("/call", methods=["POST"])
def call_tool():
    body = request.get_json() or {}
    name = body.get("name")
    args = body.get("args") or {}

    if not name:
        return jsonify({"success": False, "error": "missing 'name' in request body"}), 400

    if name not in TOOLS:
        return jsonify({"success": False, "error": f"tool '{name}' not found"}), 404

    try:
        result = TOOLS[name]["function"](args)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # runs on port 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
