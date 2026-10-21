import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
BOT_NAME = os.getenv("BOT_NAME", "QwenPokerBot")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

# FeedMeBots enforces a 2000ms response timeout.
# We set our internal deadline to 1800ms so we have 200ms headroom for HTTP/network.
DECISION_TIMEOUT_MS = int(os.getenv("DECISION_TIMEOUT_MS", "1800"))
