from twilio_whatsapp_llm.app import create_app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
