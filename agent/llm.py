import json
import re
import time
from typing import Any, Dict, Optional
import requests
from agent.config import OLLAMA_BASE_URL, OLLAMA_MODEL, DECISION_TIMEOUT_MS
from agent.prompt import SYSTEM_PROMPT, build_prompt

# Persistent HTTP session with connection pooling for sub-150ms inference calls
_session = requests.Session()

def query_ollama(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches a structured chat request to the local Ollama instance.
    Returns the parsed JSON response dictionary and latency in ms.
    """
    user_prompt = build_prompt(state)
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 30
        }
    }

    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    timeout_sec = DECISION_TIMEOUT_MS / 1000.0

    t0 = time.perf_counter()
    resp = _session.post(url, json=payload, timeout=timeout_sec)
    dt_ms = (time.perf_counter() - t0) * 1000.0

    if resp.status_code != 200:
        raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    content = data.get("message", {}).get("content", "").strip()

    # In case model wraps in markdown json blocks ```json ... ```
    if content.startswith("```"):
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            content = match.group(0)

    parsed = json.loads(content)

    return {
        "raw": parsed,
        "latency_ms": round(dt_ms, 1),
        "prompt": user_prompt
    }
