"""
chatbot.py

We will use Twilio's Python SDK to create a Whatsapp Chatbot using
Anthropic's models for conversation.

J. A. Moreno
May 2026
"""

import datetime
from langgraph.graph.state import CompiledStateGraph
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.graph.state import RunnableConfig
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents.middleware import TodoListMiddleware, SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import AIMessage
from flask import Flask, Response, request

# Load environmental variables
load_dotenv()

# Twillio client setup
client = Client()  #By default, it looks for TWILIO_ACCOUT_SID and TWILIO_AUTH_TOKEN

# Set up the Flask app
flask_app = Flask(__name__)

# LLM set up
def set_up_llm():
    # Initialize base model
    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",  # Budget choice for this task
        temperature=0.1,  # We want answers to be a bit creative
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

@tool
def get_today_date():
    """Returns today's date"""
    return datetime.datetime.today().strftime('%y-%m-%d')


# Set up agent
def setup_agent() -> CompiledStateGraph:

    llm = set_up_llm()
    tools = [create_appointment, find_appointment, add_numbers, get_today_date]

    system_prompt = """
You are a helpful English-Spanish speaking assistant.
You will provide answers in the same language the query is.
If necessary, use the provided tools to generate your answer.
"""
    
    # Create agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[TodoListMiddleware(),
                    SummarizationMiddleware(model=llm,
                                            trigger=("tokens", 2000),
                                            keep=("messages", 10)
                                            )
                    ],
        checkpointer=InMemorySaver(),
    )

    return agent

def extract_text_from_message(message):
    content = message.content
    
    if isinstance(content, str):
        # Case 1: Simple string content
        return content
    
    elif isinstance(content, list):
        # Case 2: Multimodal content (list of dicts)
        # Iterate and join all 'text' blocks
        text_parts = [
            item.get("text", "") 
            for item in content 
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return " ".join(text_parts)
    
    return ""


# Create the agent
agent = setup_agent()


# Set up Flask endpoints
@flask_app.route("/whatsapp", methods=["POST"])
def whatsapp_response():
    # Get user details
    reply_number = request.form.get("From")
    message = request.form.get("Body")

    # Define configuration
    config = RunnableConfig(
        {
            "configurable": {
                    "thread_id": reply_number  # Change later
            }
        }
    )
    # Form message
    messages = [{"role": "user", "content": message}]

    # Call agent
    model_response = agent.invoke(
                {"messages": messages},
                config=config
    )

    # Reply to user in whatsapp
    reply = MessagingResponse()
    ai_messages = [message for message in model_response["messages"] if isinstance(message, AIMessage)]
    ai_text = list(map(extract_text_from_message, ai_messages))
    outputs = "\n".join(ai_text)
    reply.message(outputs)
    return Response(str(reply), mimetype='text/xml')

# Run the application
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080, debug=True)
