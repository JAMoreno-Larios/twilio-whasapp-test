from flask import Blueprint, Response, request
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from twilio.twiml.messaging_response import MessagingResponse

from twilio_whatsapp_llm.agent.factory import extract_reply_text

whatsapp_bp = Blueprint("whatsapp", __name__)


def init_whatsapp_routes(agent: CompiledStateGraph) -> Blueprint:
    @whatsapp_bp.route("/whatsapp", methods=["POST"])
    def whatsapp_response():
        reply_number = request.form.get("From")
        message = request.form.get("Body")

        config = RunnableConfig(configurable={"thread_id": reply_number})
        messages = [{"role": "user", "content": message}]

        model_response = agent.invoke({"messages": messages}, config=config)

        reply = MessagingResponse()
        reply.message(extract_reply_text(model_response))
        return Response(str(reply), mimetype="text/xml")

    return whatsapp_bp
