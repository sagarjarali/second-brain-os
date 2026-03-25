from openai import OpenAI
from dotenv import load_dotenv
import os

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

def get_relevant_scheme(question):
    q = question.lower()

    for s in schemes:
        if any(word in s.lower() for word in q.split() if len(word) > 3):
            return s

    return schemes[0] if schemes else ""

def ask_ai(question):
    context = get_relevant_scheme(question)

    prompt = f"""
ನೀವು ಉತ್ತರ ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸ್ನೇಹಪೂರ್ಣ ಸಹಾಯಕ.

ನಿಯಮಗಳು:
- ಸರಳ ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ
- ಉತ್ತರ ಕರ್ನಾಟಕದ ಮಾತಿನ ಶೈಲಿ ಬಳಸಿ
- ಪುಸ್ತಕದ ಕನ್ನಡ ಬೇಡ
- 3 ರಿಂದ 4 ಚಿಕ್ಕ ವಾಕ್ಯಗಳಲ್ಲಿ ಉತ್ತರಿಸಿ
- ವಾಕ್ಯಗಳನ್ನು ಪೂರ್ಣವಾಗಿ ಮುಗಿಸಿ
- ಮಧ್ಯದಲ್ಲಿ ನಿಲ್ಲಿಸಬೇಡಿ
- ಅನಗತ್ಯ ಪರಿಚಯ ಬೇಡ

ಮಾಹಿತಿ:
{context}

ರೈತನ ಪ್ರಶ್ನೆ:
{question}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You help Karnataka farmers in simple spoken Kannada."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=220,
            temperature=0.3
        )

        answer = response.choices[0].message.content.strip()

        return answer

    except Exception as e:
        print("AI ERROR:", e)
        return "ಸ್ವಲ್ಪ ತೊಂದರೆ ಇದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."