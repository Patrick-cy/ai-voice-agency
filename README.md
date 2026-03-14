# AI Voice Agency

An AI-powered voice agency that handles inbound phone calls using **OpenAI** language models and **Twilio** telephony. When a caller rings in, the system greets them, transcribes their speech, feeds it to a GPT model, and reads the response back — all in real time.

---

## Architecture

```
Twilio (PSTN) ──► POST /voice/inbound     ← new call arrives
                  POST /voice/speech/{sid} ← caller has spoken
                  POST /voice/status       ← call lifecycle events

Each request ──► FastAPI ──► AIAgent ──► OpenAI Chat API
                                │
                         ConversationState (in-memory)
```

### Key modules

| File | Responsibility |
|---|---|
| `app/main.py` | FastAPI application & Twilio webhook handlers |
| `app/agent.py` | Conversation state management and OpenAI integration |
| `app/voice.py` | TwiML builders (Gather / Say / Hangup) |
| `app/models.py` | Pydantic models shared across the application |
| `app/config.py` | Environment-based configuration via pydantic-settings |

---

## Quick start

### 1. Clone & install

```bash
git clone https://github.com/Patrick-cy/ai-voice-agency.git
cd ai-voice-agency
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY, TWILIO_* credentials, and APP_BASE_URL
```

### 3. Run locally

```bash
uvicorn app.main:app --reload
```

Expose it to the internet with [ngrok](https://ngrok.com/):

```bash
ngrok http 8000
# Then set APP_BASE_URL=https://<ngrok-id>.ngrok.io in .env
```

### 4. Configure Twilio

In your Twilio phone number settings set:

- **Voice → A call comes in → Webhook**: `https://<your-domain>/voice/inbound`
- **Voice → Call status changes**: `https://<your-domain>/voice/status`

---

## Docker

```bash
docker-compose up --build
```

---

## Running tests

```bash
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | OpenAI secret key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model to use |
| `TWILIO_ACCOUNT_SID` | *(required)* | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | *(required)* | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | *(required)* | Your Twilio phone number |
| `APP_BASE_URL` | `http://localhost:8000` | Public base URL for callback URLs |
| `LOG_LEVEL` | `INFO` | Python log level |
| `MAX_CONVERSATION_TURNS` | `10` | Max turns before the call is ended |

---

## License

MIT

