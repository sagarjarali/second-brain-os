import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# -------- GLOBAL CACHE --------
embedding_model = None
collection = None
client = None
history = [
    {
        "role": "system",
        "content": "You are a helpful assistant for Karnataka farmers. Keep answers simple and practical."
    }
]

# -------- INIT FUNCTION --------
def init_brain():
    global embedding_model, collection, client

    if embedding_model is None:
        print("Loading embedding model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    if collection is None:
        print("Connecting to ChromaDB...")
        chroma_client = chromadb.Client()
        collection = chroma_client.get_or_create_collection(name="schemes")

        if collection.count() == 0:
            print("Loading schemes into vector DB...")
            with open("schemes.txt", "r") as file:
                text = file.read()

            chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

            for i, chunk in enumerate(chunks):
                emb = embedding_model.encode(chunk).tolist()
                collection.add(
                    ids=[str(i)],
                    embeddings=[emb],
                    documents=[chunk]
                )

            print("Schemes loaded.")

    if client is None:
        print("Connecting to Groq...")
        api_key = os.getenv("GROQ_API_KEY")
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )

# -------- RAG --------
def get_relevant_schemes(question):
    init_brain()

    question_embedding = embedding_model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=2
    )

    schemes = results["documents"][0]
    return "\n\n".join(schemes)

# -------- MAIN AI --------
def ask_ai(question):
    init_brain()

    context = get_relevant_schemes(question)

    prompt = f"""Use this information to answer:

{context}

Question: {question}"""

    history.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history
    )

    answer = response.choices[0].message.content

    history.append({"role": "assistant", "content": answer})

    return answer