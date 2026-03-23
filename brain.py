from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

def load_schemes():
    with open("schemes.txt", "r") as file:
        text = file.read()
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return chunks

schemes = load_schemes()

history = [
    {
        "role": "system",
        "content": "You are a helpful assistant for Karnataka farmers. Keep answers simple and practical."
    }
]

def get_relevant_schemes(question):
    question_lower = question.lower()
    relevant = []
    for scheme in schemes:
        scheme_lower = scheme.lower()
        words = question_lower.split()
        for word in words:
            if len(word) > 3 and word in scheme_lower:
                if scheme not in relevant:
                    relevant.append(scheme)
                break
    if not relevant:
        relevant = schemes[:3]
    context = "\n\n".join(relevant[:3])
    return context

def ask_ai(question):
    context = get_relevant_schemes(question)

    question_with_context = f"""Use this information to answer the question:

{context}

Question: {question}"""

    history.append({
        "role": "user",
        "content": question_with_context
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history
    )

    answer = response.choices[0].message.content

    history.append({
        "role": "assistant",
        "content": answer
    })

    return answer

if __name__ == "__main__":
    while True:
        question = input("You: ")
        answer = ask_ai(question)
        print("AI:", answer)
        print()