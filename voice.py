import requests
from groq import Groq
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(audio_url, twilio_sid, twilio_token):
    audio_data = requests.get(
        audio_url,
        auth=(twilio_sid, twilio_token)
    )
    with open("audio.ogg", "wb") as f:
        f.write(audio_data.content)
    
    with open("audio.ogg", "rb") as f:
        transcription = groq_client.audio.transcriptions.create(
            file=("audio.ogg", f.read()),
            model="whisper-large-v3",
            language="kn"
        )
    
    return transcription.text

def translate_to_english(kannada_text):
    english_text = GoogleTranslator(source="kn", target="en").translate(kannada_text)
    return english_text

def translate_to_kannada(english_text):
    kannada_text = GoogleTranslator(source="en", target="kn").translate(english_text)
    return kannada_text
