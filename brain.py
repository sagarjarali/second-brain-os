from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------- LOAD SCHEMES ----------
def load_schemes():
    try:
        with open("schemes.txt", "r", encoding="utf-8") as f:
            text = f.read()
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        return chunks
    except:
        return []

schemes = load_schemes()

# ---------- LIGHT RETRIEVAL ----------
def get_relevant_scheme(question):
    q = question.lower()

    for s in schemes:
        if any(word in s.lower() for word in q.split() if len(word) > 3):
            return s

    # fallback
    return schemes[0] if schemes else ""


# ---------- MAIN AI ----------
def ask_ai(question):

    context = get_relevant_scheme(question)

    prompt = f"""
ನೀವು ಉತ್ತರ ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸ್ನೇಹಪೂರ್ಣ ಕೃಷಿ ಸಹಾಯಕ.

ಸರಳವಾಗಿ ಮಾತನಾಡಿ.
ಹಳ್ಳಿ ಶೈಲಿಯಲ್ಲಿ ಉತ್ತರ ನೀಡಿ.
ಚಿಕ್ಕ ವಾಕ್ಯ ಬಳಸಿ.
ಪುಸ್ತಕದ ಕನ್ನಡ ಬೇಡ.

ಮಾಹಿತಿ:
{context}

ರೈತರ ಪ್ರಶ್ನೆ:
{question}

ಉತ್ತರವನ್ನು 4–5 ಸಾಲಿನೊಳಗೆ ನೀಡಿ.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You help Karnataka farmers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.4
        )

        answer = response.choices[0].message.content
        return answer

    except Exception as e:
        print("AI ERROR:", e)
        return "ಸ್ವಲ್ಪ ತೊಂದರೆ ಇದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."