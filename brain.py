import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import os

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./schemes_db")
collection = chroma_client.get_or_create_collection(name="schemes")

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

history = [
    {
        "role": "system",
        "content": "You are a helpful assistant for Karnataka farmers. Keep answers simple and practical."
    }
]

def get_relevant_schemes(question):
    question_embedding = embedding_model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=2
    )
    schemes = results['documents'][0]
    context = "\n\n".join(schemes)
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