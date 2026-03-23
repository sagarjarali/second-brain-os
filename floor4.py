from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

response = client.chat.completions.create(
    model="google/gemma-3-4b-it:free",
    messages=[
        {
            "role": "user",
            "content": "What is the best crop to grow in Karnataka during kharif season?"
        }
    ]
)

print(response.choices[0].message.content)