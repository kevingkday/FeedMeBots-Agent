# FeedMeBots AI Agent 🤖♠️

An autonomous local LLM poker bot designed to compete in the **FeedMeBots** arena.
Powered by **Qwen 2.5 7B Instruct** running locally via **Ollama** on your **NVIDIA GeForce RTX 5080**.

---

## Architecture Overview

```
FeedMeBots Platform (Arena)
       │
       │ HTTP POST /action (PlayerGameStateV1)
       ▼
FeedMeBots-Agent (FastAPI :8080)
       │
       │ Structured Prompt
       ▼
Local Ollama (Qwen 2.5 7B Instruct / RTX 5080)
       │
       │ JSON { "action": "raise", "amount": 400 }
       ▼
Validator & Legal Sizing Safeguard (Clamps min/max raise, prevents timeouts)
       │
       └────▶ HTTP 200 Response (FeedMeBotsActionV1)
```

---

## 1. Quick Start

### Prerequisites
1. **Python 3.10+**
2. **Ollama** running locally with `qwen2.5:7b-instruct` installed:
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Agent Server
```bash
python server.py
# Listening on http://0.0.0.0:8080
```

---

## 2. Test Connection & Legality

Run the self-test suite to simulate 3 live poker scenarios against your local Ollama:
```bash
python test_agent.py
```

You can also test the live HTTP endpoint directly:
```bash
curl http://localhost:8080/health
```

---

## 3. Connect to FeedMeBots Arena

### Option A: Local Test Bench (Single Hand Verification)
1. Open the FeedMeBots web dashboard at **http://localhost:3001**
2. In the **Test Connection** card, enter:
   - Webhook URL: `http://localhost:8080`
3. Click **Test Hand**. FeedMeBots will play a live hand against a house bot and show latency and payloads!

### Option B: Local Tournament / Table Runner
Register your bot endpoint in FeedMeBots:
```bash
curl -X POST http://localhost:3001/api/bots/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Qwen5080", "webhookUrl": "http://localhost:8080"}'
```

### Option C: Cloudflare Edge Arena via Tunnel
If playing against the hosted Cloudflare Workers arena:
```bash
cloudflared tunnel --url http://localhost:8080
```
Then register the generated `https://xxxx.trycloudflare.com` URL in the tournament!

---

## 4. Fine-Tuning on RTX 5080 (16GB VRAM)

### Step 1: Generate Training Hands from the Simulator
Inside the `FeedMeBots` repository, generate 10,000 tournament hands:
```bash
pnpm dev:sim --hands 10000 --bots tag,tag,station,random --export data/hands.json
```

### Step 2: Prepare JSONL Instruction Dataset
Inside `FeedMeBots-Agent`:
```bash
python train/prepare_data.py --input ../FeedMeBots/data/hands.json --output data/train.jsonl
```

### Step 3: Run QLoRA Fine-Tuning
```bash
pip install -r requirements-train.txt
python train/finetune_unsloth.py
```
This produces `outputs/gguf/unsloth.Q4_K_M.gguf`.

### Step 4: Import into Ollama
```bash
ollama create feedme-qwen -f train/Modelfile
```
Update `.env` to use your custom fine-tuned model:
```bash
OLLAMA_MODEL=feedme-qwen
```
