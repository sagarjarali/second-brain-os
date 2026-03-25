from flask import Flask, request
from dotenv import load_dotenv
import os
import threading
from twilio.rest import Client

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return "Second Brain OS running", 200


def process_voice_and_reply(media_url, twilio_sid, twilio_token, sender_number):
    try:
        print("Voice processing started")

        from voice import transcribe_audio, translate_to_english, translate_to_kannada
        from brain import ask_ai

        kannada_text = transcribe_audio(media_url, twilio_sid, twilio_token)
        english_text = translate_to_english(kannada_text)
        english_answer = ask_ai(english_text)
        response_text = translate_to_kannada(english_answer)

    except Exception as e:
        print("VOICE ERROR:", e)
        response_text = "ಕ್ಷಮಿಸಿ, ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."

    try:
        client = Client(twilio_sid, twilio_token)
        client.messages.create(
            from_="whatsapp:+14155238886",
            to=sender_number,
            body=response_text
        )
    except Exception as e:
        print("TWILIO SEND ERROR:", e)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        incoming_message = request.values.get("Body", "").strip()
        media_url = request.values.get("MediaUrl0", "")
        sender_number = request.values.get("From", "")

        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")

        if media_url:
            thread = threading.Thread(
                target=process_voice_and_reply,
                args=(media_url, twilio_sid, twilio_token, sender_number),
                daemon=True
            )
            thread.start()
            return """<?xml version="1.0" encoding="UTF-8"?><Response></Response>""", 200

        from brain import ask_ai
        from voice import translate_to_english, translate_to_kannada

        if not incoming_message:
            answer = "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕಳುಹಿಸಿ."
        else:
            english_question = translate_to_english(incoming_message)
            english_answer = ask_ai(english_question)
            answer = translate_to_kannada(english_answer)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{answer}</Message>
</Response>""", 200

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Server error. Try again.</Message>
</Response>""", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)