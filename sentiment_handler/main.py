import base64
import json
import logging
import os
from typing import Any

import functions_framework
import requests
from flask import Request
from google.cloud import language_v1
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = os.environ["PROJECT_ID"]
TARGET_SENTIMENT = os.environ["TARGET_SENTIMENT"]  # positive or negative
SLACK_WEBHOOK_SECRET = os.environ["SLACK_WEBHOOK_SECRET"]

language_client = language_v1.LanguageServiceClient()
secret_client = secretmanager.SecretManagerServiceClient()


def get_secret(secret_id: str) -> str:
    secret_path = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_path})
    return response.payload.data.decode("utf-8")


def classify_sentiment(text: str) -> tuple[str, float, float]:
    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT,
    )

    response = language_client.analyze_sentiment(request={"document": document})

    score = response.document_sentiment.score
    magnitude = response.document_sentiment.magnitude

    if score >= 0.25:
        label = "positive"
    elif score <= -0.25:
        label = "negative"
    else:
        label = "neutral"

    return label, score, magnitude


def send_slack_alert(
    webhook_url: str, user_id: str, message: str, score: float, magnitude: float
):
    slack_payload = {
        "text": (
            f"*{TARGET_SENTIMENT.upper()} feedback detected*\n"
            f"*User:* `{user_id}`\n"
            f"*Message:* {message}\n"
            f"*Score:* `{score}`\n"
            f"*Magnitude:* `{magnitude}`"
        )
    }

    response = requests.post(webhook_url, json=slack_payload, timeout=10)
    response.raise_for_status()


@functions_framework.http
def handle_feedback(request: Request):
    try:
        envelope: dict[str, Any] = request.get_json(silent=False)
    except Exception:
        logger.exception("Invalid Pub/Sub push payload")
        return "Bad Request", 400

    pubsub_message = envelope.get("message", {})
    encoded_data = pubsub_message.get("data")

    if not encoded_data:
        logger.warning("No data in Pub/Sub message")
        return "No data", 204

    try:
        decoded = base64.b64decode(encoded_data).decode("utf-8")
        payload = json.loads(decoded)
    except Exception:
        logger.exception("Failed to decode Pub/Sub message")
        return "Invalid message", 400

    user_id = payload.get("user_id", "unknown")
    message = payload.get("message", "")

    if not message:
        logger.warning("Empty message received")
        return "Empty message", 204

    label, score, magnitude = classify_sentiment(message)

    logger.info(
        "Sentiment result: label=%s target=%s score=%s magnitude=%s",
        label,
        TARGET_SENTIMENT,
        score,
        magnitude,
    )

    if label != TARGET_SENTIMENT:
        logger.info("Ignoring %s message in %s handler", label, TARGET_SENTIMENT)
        return "Ignored", 204

    webhook_url = get_secret(SLACK_WEBHOOK_SECRET)
    send_slack_alert(webhook_url, user_id, message, score, magnitude)

    logger.info("Slack alert sent for %s feedback", TARGET_SENTIMENT)
    return "OK", 200
