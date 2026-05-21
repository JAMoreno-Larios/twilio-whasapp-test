import os

from dotenv import load_dotenv

load_dotenv()


def get_checkpointer_backend() -> str:
    return os.getenv("CHECKPOINTER_BACKEND", "memory").lower()
