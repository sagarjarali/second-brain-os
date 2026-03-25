from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def load_schemes():
    try:
        with open("schemes.txt", "r", encoding="utf-8") as f:
            text = f.read()
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        return chunks
    except Exception as e:
        print("SCHEME LOAD ERROR:", e)
        return []

schemes = load_schemes()


# ---------------------------
# SIMPLE RETRIEVAL
# ---------------------------
def get_relevant_scheme(question):
    q = question.lower()

    for s in schemes:
        if any(word in s.lower() for word in q.split() if len(word) > 3):
            return s

    return schemes[0] if schemes else ""


# ---------------------------
# SMALL RULE-BASED REPLIES
# ---------------------------
def get_canned_reply(question):
    q = question.strip().lower()

    greeting_words = [
        "hi", "hello", "namaste", "ನಮಸ್ಕಾರ", "ಹಲೋ", "hello ai"
    ]
    thanks_words = [
        "thanks", "thank you", "ಧನ್ಯವಾದ", "ಧನ್ಯವಾದಗಳು"
    ]
    help_words = [
        "ಯಾರು ನೀನು", "ನೀನು ಯಾರು", "ಏನು ಮಾಡುತ್ತೀಯ", "ಏನು ಸಹಾಯ", "help"
    ]

    if any(word in q for word in greeting_words):
        return "ನಮಸ್ಕಾರ. ನಿಮಗೆ ಯಾವ ಯೋಜನೆ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕೋ ಕೇಳಿ."

    if any(word in q for word in thanks_words):
        return "ಸರಿ. ಇನ್ನೇನಾದರೂ ಸಹಾಯ ಬೇಕಿದ್ದರೆ ಕೇಳಿ."

    if any(word in q for word in help_words):
        return "ನಾನು ರೈತರಿಗೆ ಸರ್ಕಾರಿ ಯೋಜನೆ ಮಾಹಿತಿ ಹೇಳ್ತೀನಿ. ನಿಮ್ಮ ಜಮೀನು, ಬೆಳೆ, ಅಥವಾ ಯೋಜನೆ ಬಗ್ಗೆ ಕೇಳಿ."

    return None


# ---------------------------
# CLEAN OUTPUT
# ---------------------------
def clean_answer(text):
    if not text:
        return "ಸ್ವಲ್ಪ ತೊಂದರೆ ಇದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."

    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted intro lines if model adds too much fluff
    text = text.replace("ನಮಸ್ಕಾರ,", "").strip()
    text = text.replace("ನಮಸ್ಕಾರ.", "").strip()

    # Keep only first 2 complete sentences
    parts = re.split(r'(?<=[.?!।])\s+', text)
    complete_parts = []

    for p in parts:
        p = p.strip()
        # Only add sentence if it ends with proper punctuation
        if p and p[-1] in ".?!।":
            complete_parts.append(p)
        if len(complete_parts) == 2:
            break

    if complete_parts:
        cleaned = " ".join(complete_parts).strip()
        return cleaned

    # fallback: trim to last safe punctuation mark
    last_punct = max(text.rfind("."), text.rfind("?"), text.rfind("!"), text.rfind("।"))
    if last_punct != -1:
        return text[:last_punct + 1].strip()

    # final fallback
    if len(text) > 180:
        return text[:180].strip() + "..."
    return text


# ---------------------------
# MAIN AI
# ---------------------------
def ask_ai(question):
    # 1. canned reply first
    canned = get_canned_reply(question)
    if canned:
        return canned

    # 2. scheme context
    context = get_relevant_scheme(question)

    prompt = f"""
ನೀವು ಉತ್ತರ ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸರಳ ಸಹಾಯಕ.

ಕಟ್ಟುನಿಟ್ಟಿನ ನಿಯಮಗಳು:
- ಉತ್ತರ ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಕೊಡಿ
- ಉತ್ತರ ಉತ್ತರ ಕರ್ನಾಟಕದ ಮಾತಿನ ಶೈಲಿಯಲ್ಲಿ ಇರಲಿ
- ಪುಸ್ತಕದ ಕನ್ನಡ ಬೇಡ
- ಹೆಚ್ಚು ಹೆಚ್ಚು 2 ವಾಕ್ಯ ಮಾತ್ರ
- ಪ್ರತಿ ವಾಕ್ಯ ಚಿಕ್ಕದಾಗಿರಲಿ
- ಪೂರ್ಣ ವಾಕ್ಯಗಳಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಿ
- ಮಧ್ಯದಲ್ಲಿ ನಿಲ್ಲಿಸಬೇಡಿ
- ಅನಗತ್ಯ ಮಾತು ಬೇಡ
- "ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದ" ತರಹದ ಹೆಚ್ಚುವರಿ ಮಾತು ಬೇಡ unless user greets
- ಉತ್ತರ 160 ಅಕ್ಷರಗಳೊಳಗೆ ಇರಲಿ if possible

ಮಾಹಿತಿ:
{context}

ರೈತನ ಪ್ರಶ್ನೆ:
{question}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You answer Karnataka farmer queries in very short spoken Kannada. Always finish sentences completely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=180,
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()
        return clean_answer(answer)

    except Exception as e:
        print("AI ERROR:", e)
        return "ಸ್ವಲ್ಪ ತೊಂದರೆ ಇದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."