from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_pipeline import query_rag
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    question: str

@app.post("/ask")
def query_api(input: QueryInput):
    try:
        response = query_rag(input.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
