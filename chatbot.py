"""
chatbot.py

We will use Twilio's Python SDK to create a Whatsapp Chatbot using
Anthropic's models for conversation.

J. A. Moreno
May 2026
"""

from twilio.rest import Client
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# Load environmental variables
load_dotenv()

# Twillio client setup
client = Client()  #By default, it looks for TWILIO_ACCOUT_SID and TWILIO_AUTH_TOKEN

# LLM set up
def set_up_llm():
    # Initialize base model
    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",  # Budget choice for this task
        temperature=0.0,  # We want answers to be more deterministic
    )
    return llm

# Define LLM tools
@tool
def create_appointment(date: str) -> str:
    """Creates an appointment"""
    return f"Appointment created for {date}"

@tool
def add_numbers(a:float, b:float) -> str:
    """Add two numbers"""
    return str(a + b)

@tool
def find_appointment(date: str) -> str:
    """Finds if an appointment was made for the given date"""
    return f"Appointment found for {date}"

def generate_template() -> ChatPromptTemplate:
    """Forms the chat template that will be passed to the LLM"""

    # Define system prompt
    system_prompt = """
You are a helpful English-Spanish speaking assistant.
You will provide answers in the same language the query is.
If necessary, use the provided tools to generate your answer.
"""
    
    # Generate chat prompt
    template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
    ])

    # Return template
    return template

def main():
    print("Hello from twilio-whatsapp-llm-demo!")


if __name__ == "__main__":
    main()
