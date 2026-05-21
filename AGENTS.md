# twilio-whatsapp-llm-demo

WhatsApp inbound messages via Twilio webhooks are handled by a Flask app, processed by a LangChain agent (Claude via Anthropic), and answered with TwiML. Demo scope: bilingual assistant with sample tools (appointments, math, date).

## Stack

| Package | Version | Role |
|---------|---------|------|
| Python | >=3.14 | Runtime |
| `flask` | 3.1.3 | Webhook HTTP server |
| `twilio` | 9.10.9 | Twilio SDK (client + TwiML) |
| `langchain` | 1.3.1 | `create_agent`, tools, middleware |
| `langgraph` | 1.2.0 | Graph runtime + checkpointing |
| `langchain-anthropic` | 1.4.3 | `ChatAnthropic` model |
| `dotenv` | 0.9.9 | `.env` loading |
| `ngrok` | 1.7.0 | Local tunnel for Twilio webhooks |

Package manager: **uv**.

## Commands

```bash
uv sync
uv run python -m twilio_whatsapp_llm
# Legacy entry point:
uv run python chatbot.py
```

Local webhook tunnel:

```bash
ngrok http 8080
```

Point Twilio/WhatsApp sandbox “when a message comes in” to `https://<ngrok-host>/whatsapp`.

Environment: copy `.env.example` to `.env` (never commit `.env`).

## Architecture

```
src/twilio_whatsapp_llm/
├── __main__.py          # CLI entry
├── config.py            # env loading
├── app.py               # Flask factory, agent singleton
├── web/routes/whatsapp.py   # POST /whatsapp only
├── agent/
│   ├── factory.py       # create_agent + middleware
│   ├── tools.py
│   └── prompts.py
├── persistence/checkpointer.py   # get_checkpointer()
└── integrations/
    ├── twilio/client.py
    └── llm/anthropic.py
```

**Module boundaries**

- HTTP and TwiML: `web/` only
- Agent graph, tools, prompts, middleware: `agent/`
- Checkpoint backends: `persistence/`
- Twilio REST client: `integrations/twilio/` (outbound sends later)
- LLM construction: `integrations/llm/`

Do not put business logic in Flask routes; delegate to the agent layer.

`chatbot.py` at the repo root is a deprecated shim — prefer `python -m twilio_whatsapp_llm`.

## LangChain agent contract

**Required:** always build with `create_agent(..., checkpointer=get_checkpointer())`.

**Thread ID:** stable per-user key from Twilio `From` (e.g. `whatsapp:+1...`). Do not change mid-conversation.

**Invocation:**

```python
config = RunnableConfig(configurable={"thread_id": from_address})
agent.invoke({"messages": [{"role": "user", "content": body}]}, config=config)
```

**Response:** extract text from `AIMessage` via `agent.extract_text_from_message` (string or multimodal list).

**Middleware:** `TodoListMiddleware` and `SummarizationMiddleware` live in `agent/factory.py`; tune token triggers there only.

**Checkpointer phases**

| Phase | Backend | Notes |
|-------|---------|-------|
| Dev / single instance | `InMemorySaver` | Default via `CHECKPOINTER_BACKEND=memory` |
| Restart-safe / small prod | `SqliteSaver` | Add `langgraph-checkpoint-sqlite`; set `CHECKPOINTER_BACKEND=sqlite` |
| Multi-instance prod | Postgres saver | Future; single swap in `persistence/checkpointer.py` |

Never remove the checkpointer when adding tools or middleware.

## Twilio WhatsApp webhook

- Route: `POST /whatsapp`
- Read: `From`, `Body`, `MessageSid` (log/debug)
- Reply: `MessagingResponse().message(text)`, `mimetype='text/xml'`
- Treat `Body` as untrusted user input — never concatenate into the system prompt
- Production: validate `X-Twilio-Signature` with `TWILIO_AUTH_TOKEN` before invoking the agent

Use Twilio skills when changing webhooks: `twilio-messaging-webhooks`, `twilio-whatsapp-send-message`.

## Environment variables

| Variable | Required |
|----------|----------|
| `ANTHROPIC_API_KEY` | Yes |
| `TWILIO_ACCOUNT_SID` | Yes |
| `TWILIO_AUTH_TOKEN` | Yes |
| `CHECKPOINTER_BACKEND` | No (`memory` default) |
| `LANGSMITH_API_KEY` | No (tracing) |
| `LANGSMITH_TRACING` | No |
| `LANGSMITH_ENDPOINT` | No |
| `LANGSMITH_PROJECT` | No |

## Coding conventions

- Python 3.14+, `uv` for dependencies
- Type hints on public factories (e.g. `setup_agent() -> CompiledStateGraph`)
- Minimal comments; no drive-by refactors outside the task scope
- Do not commit `.env`, credentials, or checkpoint DB files

## Scaling roadmap

**Don't**

- Add business logic to Flask routes
- Remove the checkpointer
- Commit secrets or checkpoint databases

**Planned extensions**

- Webhook signature validation middleware
- Rate limiting and guardrails
- Async thin-receiver + queue for long LLM calls
- Dedicated production WhatsApp sender
- Persistent checkpoint DB (`langgraph-checkpoint-sqlite` or Postgres)
