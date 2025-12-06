# backend.py
from mcp_client import run_once
import json

def process_prompt(prompt: str) -> str:
    """
    Synchronous entry point used by Streamlit UI.
    It calls the LLM via mcp_client and returns a readable string.
    """
    try:
        out = run_once(prompt)

        # LLM returned normal text (not a tool call)
        if out["type"] == "llm_text":
            return out["content"]

        # Tool call result
        elif out["type"] == "tool_result":
            result = out.get("result", {})
            tool = out.get("tool")

            # Extract fields from MCP response
            mcp_success = result.get("success", False)
            tool_resp = result.get("result", {})
            tool_success = tool_resp.get("success", False)
            status_code = tool_resp.get("status_code", 0)

            # If email was sent (HTTP 200)
            if mcp_success and tool_success and status_code == 200:
                return "Email Successfully Sent"

            # Otherwise return detailed error
            pretty = json.dumps(result, indent=2)
            return f"Tool '{tool}' executed with errors:\n{pretty}"
        else:
            return str(out)
    except Exception as e:
        return f"Error processing prompt: {str(e)}"
