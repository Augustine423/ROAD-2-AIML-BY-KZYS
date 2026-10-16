import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

ai_client = ChatCompletionsClient(
    endpoint=AZURE_OPENAI_ENDPOINT,
    credential=AzureKeyCredential(AZURE_OPENAI_API_KEY)
)

app = FastAPI(title="Azure AI Chat Assistant")


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = ai_client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content=req.message)
            ],
            model=MODEL_DEPLOYMENT
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/config")
async def config():
    return {"model": MODEL_DEPLOYMENT}


@app.get("/")
async def root():
    return FileResponse(str(Path(__file__).parent / "index.html"))


app.mount("/static", StaticFiles(directory=str(Path(__file__).parent)), name="static")