from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- CLIENT ----------
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
    except Exception as e:
        print("SCHEME LOAD ERROR:", e)
        return []

schemes = load_schemes()

# ---------- SIMPLE RETRIEVAL ----------
def get_relevant_schemes(question):
    q = question.lower()

    matches = []
    for s in schemes:
        s_low = s.lower()
        for w in q.split():
            if len(w) > 3 and w in s_low:
                matches.append(s)
                break

    if not matches:
        matches = schemes[:3]

    return "\n\n".join(matches[:3])


# ---------- MAIN AI ----------
def ask_ai(question):

    context = get_relevant_schemes(question)

    prompt = f"""
You are a helpful Karnataka government schemes assistant.

Answer in simple practical language.

Information:
{context}

Farmer Question:
{question}
"""

    messages = [
        {
            "role": "system",
            "content": "You help farmers understand government schemes simply."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=250,
            temperature=0.3
        )

        answer = response.choices[0].message.content
        return answer

    except Exception as e:
        print("GROQ ERROR:", e)
        return "ಕ್ಷಮಿಸಿ, ಈಗ ಸರ್ವರ್ ಸಮಸ್ಯೆ ಇದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."