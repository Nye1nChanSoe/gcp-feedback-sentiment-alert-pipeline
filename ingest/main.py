import json
import os
from typing import Any

import functions_framework
from google.cloud import pubsub_v1
from flask import Request, jsonify

PROJECT_ID = os.environ["PROJECT_ID"]
TOPIC_ID = os.environ.get("FEEDBACK_TOPIC", "feedback-topic")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


@functions_framework.http
def ingest_feedback(request: Request):
    if request.method != "POST":
        return jsonify({"error": "Only POST is allowed"}), 405

    try:
        payload: dict[str, Any] = request.get_json(silent=False)
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_id = payload.get("user_id")
    message = payload.get("message")

    if not user_id or not message:
        return jsonify(
            {
                "error": "Missing required fields",
                "required": ["user_id", "message"],
            }
        ), 400

    event = {
        "user_id": user_id,
        "message": message,
    }

    data = json.dumps(event).encode("utf-8")

    future = publisher.publish(
        topic_path,
        data,
        source="feedback-ingest-service",
    )

    message_id = future.result(timeout=10)

    return jsonify(
        {
            "status": "published",
            "message_id": message_id,
            "topic": TOPIC_ID,
            "data": event,
        }
    ), 200
