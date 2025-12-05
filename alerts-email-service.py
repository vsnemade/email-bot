import os
import smtplib
import logging
from flask import Flask, request, jsonify
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def validate_payload(data):
    if not isinstance(data, dict):
        return None, "Invalid JSON format"

    to = data.get("to")
    subject = data.get("subject")
    body = data.get("body")

    if not to or not isinstance(to, str):
        return None, "'to' must be a string"
    if not subject or not isinstance(subject, str):
        return None, "'subject' must be a string"
    if not body or not isinstance(body, str):
        return None, "'body' must be a string"

    return {
        "to": to,
        "subject": subject,
        "body": body
    }, None


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()

    payload, error = validate_payload(data)
    if error:
        return jsonify({"error": error}), 400

    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = payload["to"]
    msg["Subject"] = payload["subject"]
    msg.set_content(payload["body"])

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"status": "sent"}), 200

    except Exception as e:
        logging.exception("Failed to send email")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
