from flask import Flask
from langgraph.graph.state import CompiledStateGraph

from twilio_whatsapp_llm.agent.factory import setup_agent
from twilio_whatsapp_llm.web.routes.whatsapp import init_whatsapp_routes


def create_app(agent: CompiledStateGraph | None = None) -> Flask:
    app = Flask(__name__)
    if agent is None:
        agent = setup_agent()
    app.register_blueprint(init_whatsapp_routes(agent))
    return app
