# GCP Feedback Sentiment Alert Pipeline

An event-driven serverless feedback processing pipeline built on Google Cloud Platform.

The system receives user feedback through an HTTP endpoint, publishes the message to Pub/Sub, analyzes sentiment using Google Cloud Natural Language API, and sends Slack alerts based on whether the feedback is positive or negative.

---

## Architecture

```text
Postman / Client
      ↓
feedback-ingest-service
      ↓ publishes message
feedback-topic
      ↓                         ↓
positive-sub                negative-sub
      ↓                         ↓
positive-feedback-handler   negative-feedback-handler
      ↓                         ↓
Slack #followup             Slack #support
```