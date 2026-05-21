from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from twilio_whatsapp_llm.config import get_checkpointer_backend


def get_checkpointer() -> BaseCheckpointSaver:
    backend = get_checkpointer_backend()
    if backend == "memory":
        return InMemorySaver()
    if backend == "sqlite":
        raise NotImplementedError(
            "SqliteSaver requires langgraph-checkpoint-sqlite; "
            "add the dependency and implement persistence here."
        )
    raise ValueError(f"Unknown CHECKPOINTER_BACKEND: {backend}")
