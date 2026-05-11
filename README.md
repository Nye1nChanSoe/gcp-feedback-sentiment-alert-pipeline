# GCP Feedback Sentiment Alert Pipeline

## Overview

The GCP Feedback Sentiment Alert Pipeline is an event-driven serverless application built on Google Cloud Platform that processes user feedback asynchronously using Pub/Sub messaging and Google Cloud Natural Language API.

The system receives incoming feedback messages through an HTTP endpoint, performs sentiment analysis, and dispatches alerts to different Slack channels depending on the detected sentiment.

This project demonstrates practical cloud engineering concepts including:

- Event-driven architectures
- Serverless deployments
- Asynchronous processing
- IAM and security best practices
- Secret management
- Cloud-native observability
- CI/CD automation using Cloud Build
- Infrastructure consistency and scalability

The project is designed as a production-oriented portfolio project suitable for demonstrating modern cloud engineering practices.

---

# Architecture

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

---

# Event Flow

1. Client sends feedback message to the ingestion endpoint.
2. The ingestion service validates the payload.
3. Message is published to Pub/Sub topic `feedback-topic`.
4. Pub/Sub push subscriptions forward events to sentiment handlers.
5. Sentiment handlers analyze message sentiment using Google Cloud Natural Language API.
6. Positive and negative messages trigger Slack alerts.
7. Neutral messages are ignored or logged.

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Google Cloud Run | Serverless container hosting |
| Google Pub/Sub | Event-driven messaging |
| Google Secret Manager | Secure secret storage |
| Google Cloud Natural Language API | Sentiment analysis |
| Google Cloud Build | CI/CD pipeline |
| Artifact Registry | Docker image storage |
| Docker | Containerization |
| Python 3.12 | Application runtime |
| uv | Dependency management |
| Slack Incoming Webhooks | Notification delivery |

---

# Repository Structure

```text
.
├── cloudbuild.yaml
├── ingest
│   ├── Dockerfile
│   ├── main.py
│   ├── pyproject.toml
│   └── uv.lock
├── sentiment_handler
│   ├── Dockerfile
│   ├── main.py
│   ├── pyproject.toml
│   └── uv.lock
└── README.md
```

---

# Services

## feedback-ingest-service

Cloud Run service responsible for receiving incoming feedback requests and publishing messages to Pub/Sub.

### Responsibilities

- Expose HTTP endpoint
- Validate payloads
- Publish events to Pub/Sub
- Decouple ingestion from downstream processing

### Example Request

```json
{
  "user_id": "alice",
  "message": "This app is amazing!"
}
```

---

## positive-feedback-handler

Cloud Run service triggered by Pub/Sub push subscription `positive-sub`.

### Responsibilities

- Receive Pub/Sub events
- Analyze sentiment
- Process only positive sentiment
- Retrieve Slack webhook from Secret Manager
- Send Slack alert to `#followup`

---

## negative-feedback-handler

Cloud Run service triggered by Pub/Sub push subscription `negative-sub`.

### Responsibilities

- Receive Pub/Sub events
- Analyze sentiment
- Process only negative sentiment
- Retrieve Slack webhook from Secret Manager
- Send Slack alert to `#support`

---

# Event-Driven Architecture

This project follows an event-driven architecture pattern using Google Pub/Sub as the message bus.

## Concepts

### Producer

The ingestion service acts as the producer by publishing events into Pub/Sub.

### Message Bus

Pub/Sub acts as the asynchronous messaging backbone between services.

### Consumers

Sentiment handlers independently consume and process events.

---

## Why Event-Driven Architecture?

### Decoupling

The ingestion service does not need to know:

- Slack webhook logic
- sentiment analysis implementation
- downstream processing details

This separation improves maintainability and scalability.

---

### Asynchronous Processing

Requests are processed asynchronously through Pub/Sub, reducing coupling and improving reliability.

---

### Fan-Out Pattern

Multiple subscriptions can consume the same event independently.

This enables:

- analytics pipelines
- alerting systems
- data warehousing
- audit logging
- machine learning pipelines

without modifying the ingestion service.

---

# Sentiment Analysis Logic

The system uses Google Cloud Natural Language API for sentiment analysis.

## Sentiment Thresholds

```text
score >= 0.25   → positive
score <= -0.25  → negative
otherwise       → neutral
```

---

## Processing Logic

### Positive Feedback

- Forwarded to Slack `#followup`
- Used for customer engagement opportunities

### Negative Feedback

- Forwarded to Slack `#support`
- Used for rapid incident response

### Neutral Feedback

- Ignored or logged only

---

# Deployment Architecture

## Cloud Build Pipeline

Cloud Build automates the deployment lifecycle.

### Responsibilities

- Build Docker images
- Push images to Artifact Registry
- Deploy Cloud Run services
- Create Pub/Sub topics
- Create Pub/Sub push subscriptions

---

## Why Cloud Build?

Cloud Build is preferred over manual deployment because it provides:

### Repeatability

Consistent deployments across environments.

### CI/CD Readiness

Can integrate with GitHub triggers and automated deployments.

### Infrastructure Consistency

Ensures services, topics, and subscriptions are created consistently.

---

# Cloud Build Steps

Expected pipeline stages:

```text
create-feedback-topic
build-ingest
push-ingest
deploy-ingest
build-sentiment-handler
push-sentiment-handler
deploy-positive-handler
deploy-negative-handler
create-positive-sub
create-negative-sub
```

---

# Runtime Service Account

```text
feedback-pipeline-runtime-sa
```

Dedicated runtime service accounts improve security by granting only the minimum required permissions.

---

## IAM Roles

| Role | Purpose |
|---|---|
| pubsub.publisher | Publish messages to Pub/Sub |
| pubsub.subscriber | Consume Pub/Sub push messages |
| secretmanager.secretAccessor | Access Slack webhook secrets |
| run.invoker | Allow Cloud Run invocation |
| logging.logWriter | Write logs to Cloud Logging |
| monitoring.metricWriter | Publish monitoring metrics |
| serviceusage.serviceUsageConsumer | Access Google APIs |

---

# Secret Manager

Slack webhook URLs are securely stored in Google Secret Manager.

## Secrets

```text
slack-followup-webhook
slack-support-webhook
```

---

## Why Secret Manager?

Secrets should never be:

- hardcoded in source code
- committed to Git repositories
- stored in Docker images

Secret Manager provides centralized and secure secret access.

---

# Pub/Sub Topics and Subscriptions

## Topic

```text
feedback-topic
```

---

## Push Subscriptions

```text
positive-sub
negative-sub
```

Pub/Sub push subscriptions automatically invoke Cloud Run services.

---

# Local Development

## Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Install Dependencies

```bash
uv sync
```

---

## Run Locally

```bash
uv run python main.py
```

---

## Local Docker Testing

```bash
docker build -t feedback-ingest .
docker run -p 8080:8080 feedback-ingest
```

---

# Deployment

## Build and Deploy

```bash
gcloud builds submit --config cloudbuild.yaml .
```

---

# Testing

## Positive Feedback

```bash
curl -X POST https://YOUR_INGEST_URL \
-H "Content-Type: application/json" \
-d '{
  "user_id": "alice",
  "message": "This app is amazing. I love using it every day."
}'
```

---

## Negative Feedback

```bash
curl -X POST https://YOUR_INGEST_URL \
-H "Content-Type: application/json" \
-d '{
  "user_id": "bob",
  "message": "The service keeps crashing and support is terrible."
}'
```

---

## Neutral Feedback

```bash
curl -X POST https://YOUR_INGEST_URL \
-H "Content-Type: application/json" \
-d '{
  "user_id": "charlie",
  "message": "I used the application today."
}'
```

---

# Logging and Observability

## Cloud Logging

Cloud Run automatically streams application logs into Cloud Logging.

---

## Structured Logging

Structured JSON logging improves:

- searchability
- debugging
- monitoring
- observability

---

## View Logs

```bash
gcloud run services logs read feedback-ingest-service --region=YOUR_REGION
```

---

# Common Issues

## Pub/Sub Push Authentication Errors

### Symptoms

- 401 Unauthorized
- 403 Forbidden

### Fix

Ensure Cloud Run service allows invocation from Pub/Sub service account.

---

## Secret Manager Permission Errors

### Symptoms

```text
Permission denied on secret
```

### Fix

Grant:

```text
roles/secretmanager.secretAccessor
```

to runtime service account.

---

## Cloud Run Invoker Errors

### Symptoms

```text
The request was not authenticated
```

### Fix

Grant:

```text
roles/run.invoker
```

to Pub/Sub push identity.

---

## Docker Port Issues

### Symptoms

```text
Container failed to start and listen on port 8080
```

### Fix

Ensure application listens on:

```python
PORT = int(os.environ.get("PORT", 8080))
```

---

## Cloud Build Variable Escaping

### Symptoms

Variables substituted unexpectedly inside YAML.

### Fix

Escape variables using:

```text
$${VARIABLE}
```

---

## Artifact Registry Push Errors

### Symptoms

```text
Permission denied while pushing image
```

### Fix

Grant Artifact Registry writer permissions to Cloud Build service account.

---

# Future Improvements

Potential future enhancements include:

- BigQuery analytics pipeline
- dead-letter topics
- retry policies
- Terraform infrastructure-as-code
- monitoring dashboards
- GitHub CI/CD triggers
- centralized sentiment router service
- dedicated runtime service accounts per service
- audit logging pipeline
- Cloud Monitoring alerts

---

# Security Considerations

## Principle of Least Privilege

Runtime service accounts should only receive minimum required permissions.

---

## Secret Isolation

Sensitive credentials are isolated using Secret Manager.

---

## Service Isolation

Independent Cloud Run services reduce blast radius during failures.

---

# Scalability

This architecture scales naturally because:

- Pub/Sub buffers traffic spikes
- Cloud Run scales automatically
- consumers scale independently
- services remain loosely coupled

---

# Suggested GitHub Metadata

## Repository Name

```text
gcp-feedback-sentiment-alert-pipeline
```

---

## Repository Description

```text
Event-driven serverless feedback processing pipeline on Google Cloud Platform using Cloud Run, Pub/Sub, Secret Manager, and Natural Language API.
```

---

## Suggested Topics

```text
gcp
google-cloud
cloud-run
pubsub
serverless
docker
python
cloud-build
event-driven
slack-webhooks
sentiment-analysis
secret-manager
```

---

# Portfolio Value

This project demonstrates practical experience with:

- cloud-native architecture
- distributed systems
- asynchronous messaging
- IAM and security
- CI/CD pipelines
- containerization
- observability
- scalable serverless infrastructure

It is designed as a realistic production-oriented cloud engineering portfolio project.

