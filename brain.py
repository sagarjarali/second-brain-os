from openai import OpenAI
from dotenv import load_dotenv
import os
import re
from sentence_transformers import SentenceTransformer
import chromadb
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
embedder = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(name="schemes")

if collection.count() == 0:
    scheme_embeddings = embedder.encode(schemes).tolist()
    ids = [str(i) for i in range(len(schemes))]
    collection.add(embeddings=scheme_embeddings, documents=schemes, ids=ids)

# ---------------------------
# SIMPLE RETRIEVAL
# ---------------------------
def get_relevant_scheme(question):
    question_embedding = embedder.encode([question]).tolist()
    
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=1
    )
    
    return results['documents'][0][0]

# ---------------------------
# SMALL RULE-BASED REPLIES
# ---------------------------
def get_canned_reply(question):
    q = question.strip().lower()
    words_in_question = q.split()

    greeting_words = ["hi", "hello", "namaste", "good morning", "good evening"]
    thanks_words = ["thanks", "thank you", "thank"]
    help_words = ["who are you", "what do you do", "what can you do"]

    if any(word in words_in_question for word in greeting_words):
        return "ನಮಸ್ಕಾರ. ನಿಮಗೆ ಯಾವ ಯೋಜನೆ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕೋ ಕೇಳಿ."

    if any(word in words_in_question for word in thanks_words):
        return "ಸರಿ. ಇನ್ನೇನಾದರೂ ಸಹಾಯ ಬೇಕಿದ್ದರೆ ಕೇಳಿ."

    if any(word in words_in_question for word in help_words):
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

    parts = re.split(r'(?<=[.?!])\s+', text)
    complete_parts = []

    for p in parts:
        p = p.strip()
        if p and p[-1] in ".?!":
            complete_parts.append(p)
        if len(complete_parts) == 2:
            break

    if complete_parts:
        return " ".join(complete_parts).strip()

    last_punct = max(text.rfind("."), text.rfind("?"), text.rfind("!"))
    if last_punct != -1:
        return text[:last_punct + 1].strip()

    if len(text) > 200:
        return text[:200].strip() + "..."
    return text


# ---------------------------
# MAIN AI
# ---------------------------
def ask_ai(question):
    canned = get_canned_reply(question)
    if canned:
        return canned

    context = get_relevant_scheme(question)

    prompt = f"""
You are a helpful assistant for Karnataka farmers.

Rules:
- Answer in simple English only
- Maximum 2 sentences
- Be specific, mention scheme names and benefit amounts
- Complete sentences only
- No greetings or extra words

Scheme Information:
{context}

Farmer's Question:
{question}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Karnataka farmer assistant. Answer in simple English. Always give specific scheme names and benefit amounts. Complete every sentence."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=250,
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()
        return clean_answer(answer)

    except Exception as e:
        print("AI ERROR:", e)
        return "ಸ್ವಲ್ಪ ತೊಂದರೆ ಇದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
    
if __name__ == "__main__":
    test = "my crops are dying due to lack of water"
    result = get_relevant_scheme(test)
    print("MATCHED SCHEME:")
    print(result)