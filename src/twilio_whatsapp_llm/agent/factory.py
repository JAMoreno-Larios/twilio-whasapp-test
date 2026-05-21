from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware
from langchain.messages import AIMessage
from langgraph.graph.state import CompiledStateGraph

from twilio_whatsapp_llm.agent.prompts import SYSTEM_PROMPT
from twilio_whatsapp_llm.agent.tools import TOOLS
from twilio_whatsapp_llm.integrations.llm.anthropic import set_up_llm
from twilio_whatsapp_llm.persistence.checkpointer import get_checkpointer


def setup_agent() -> CompiledStateGraph:
    llm = set_up_llm()
    agent = create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            TodoListMiddleware(),
            SummarizationMiddleware(
                model=llm,
                trigger=("tokens", 2000),
                keep=("messages", 10),
            ),
        ],
        checkpointer=get_checkpointer(),
    )
    return agent


def extract_text_from_message(message) -> str:
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return " ".join(text_parts)

    return ""


def extract_reply_text(model_response: dict) -> str:
    ai_messages = [
        message
        for message in model_response["messages"]
        if isinstance(message, AIMessage)
    ]
    ai_text = [extract_text_from_message(message) for message in ai_messages]
    return "\n".join(ai_text)
