from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

EMAIL_API_URL = "http://localhost:5000/send-email"  # Your working email API

class EmailRequest(BaseModel):
    to: str
    body: str
    subject: str

@app.post("/process-email")
def process_email(request: EmailRequest):
    try:
        response = requests.post(EMAIL_API_URL, json={
            "to": request.to,
            "subject": request.subject,
            "body": request.body
        })
        if response.status_code == 200:
            return {"status": "Email sent successfully!"}
        else:
            return {"status": "Failed to send email", "details": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run MCP server with:
# uvicorn mcp_server:app --reload --port 8000
