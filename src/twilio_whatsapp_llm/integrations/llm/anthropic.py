from langchain_anthropic import ChatAnthropic


def set_up_llm() -> ChatAnthropic:
    return ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        temperature=0.1,
    )
