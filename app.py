from flask import Flask, request
from voice import transcribe_audio, translate_to_english, translate_to_kannada
from brain import ask_ai
from dotenv import load_dotenv
import os
import threading
from twilio.rest import Client

load_dotenv()

app = Flask(__name__)

def process_voice_and_reply(media_url, twilio_sid, twilio_token, sender_number):
    try:
        print("Starting voice processing...")
        kannada_text = transcribe_audio(media_url, twilio_sid, twilio_token)
        print("Transcribed:", kannada_text)
        english_text = translate_to_english(kannada_text)
        print("Translated:", english_text)
        english_answer = ask_ai(english_text)
        print("AI answered:", english_answer)
        response_text = translate_to_kannada(english_answer)
        print("Final Kannada:", response_text)
    except Exception as e:
        print("ERROR:", e)
        response_text = "ಕ್ಷಮಿಸಿ, ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."

    client = Client(twilio_sid, twilio_token)
    client.messages.create(
        from_="whatsapp:+14155238886",
        to=sender_number,
        body=response_text
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Received:", request.values)
    incoming_message = request.values.get("Body", "")
    media_url = request.values.get("MediaUrl0", "")
    sender_number = request.values.get("From", "")

    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")

    if media_url:
        thread = threading.Thread(
            target=process_voice_and_reply,
            args=(media_url, twilio_sid, twilio_token, sender_number)
        )
        thread.start()
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>"""
    else:
        response_text = ask_ai(incoming_message)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
