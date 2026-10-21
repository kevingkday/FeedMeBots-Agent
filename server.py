from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from agent.config import BOT_NAME, OLLAMA_MODEL, PORT, HOST
from agent.bot import decide

app = FastAPI(
    title=f"{BOT_NAME} - FeedMeBots AI Agent",
    description="Autonomous local LLM agent playing Texas Hold'em in the FeedMeBots arena."
)

class BotActionResponse(BaseModel):
    action: str
    amount: Optional[int] = None

@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "botName": BOT_NAME,
        "model": OLLAMA_MODEL,
        "engineTarget": "FeedMeBots V1"
    }

@app.post("/", response_model=BotActionResponse)
@app.post("/action", response_model=BotActionResponse)
def handle_action(state: Dict[str, Any]):
    return decide(state)

if __name__ == "__main__":
    print(f"🚀 Starting {BOT_NAME} on http://{HOST}:{PORT}")
    print(f"🧠 Local Model Target: {OLLAMA_MODEL}")
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
