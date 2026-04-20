from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Second Brain OS running"}

from pydantic import BaseModel

class QuestionRequest(BaseModel):
   question: str
   
@app.post("/ask")
def ask_farmer_question(request: QuestionRequest):
    from brain import get_relevant_scheme
    scheme = get_relevant_scheme(request.question)
    return {"scheme": scheme}