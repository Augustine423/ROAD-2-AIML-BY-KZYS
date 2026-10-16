# Azure Generative AI Chat

A simple chat app powered by Azure AI Foundry with FastAPI backend.

![Chat UI](chat-ui.png)

## Setup

```bash
pip install -r requirements.txt
```

## Configure

Edit `.env`:

```
AZURE_OPENAI_ENDPOINT="https://your-resource.services.ai.azure.com/models"
MODEL_DEPLOYMENT="gpt-5.2"
AZURE_OPENAI_API_KEY="your-api-key"
```

## Run

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000**

## Docker

```bash
docker build -t azure-genai-chat .
docker run -p 8000:8000 azure-genai-chat
```

## Kubernetes

```bash
kubectl apply -f deploy.yaml
```