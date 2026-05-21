# twilio-whatsapp-llm-demo

Flask app that links WhatsApp messages received through Twilio to a LangChain agent (Claude via Anthropic).

**AI coding agents:** read [AGENTS.md](AGENTS.md) for stack, conventions, and module layout.

## Prior requirements

- Twilio account with WhatsApp sandbox or sender configured
- Anthropic API key

## Installation

```bash
uv sync
cp .env.example .env
# Edit .env with your keys
```

## Run

```bash
uv run python -m twilio_whatsapp_llm
```

Expose locally for Twilio webhooks:

```bash
ngrok http 8080
```

Set the sandbox webhook URL to `https://<ngrok-host>/whatsapp`.

## Stack

- Flask
- LangChain + LangGraph (checkpointer)
- Twilio Python SDK
- Anthropic (Claude)
- uv for package management
- ngrok for local routing

## Next steps

- Deploy to cloud
- Webhook signature validation
- Guardrails and rate limiting
- Persistent checkpointer (`langgraph-checkpoint-sqlite`)
- Dedicated Twilio WhatsApp number for production
