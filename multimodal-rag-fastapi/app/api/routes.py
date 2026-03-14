from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.rag_service import rag_service

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/embed")
def embed_files(background_tasks: BackgroundTasks):
    if rag_service.embedding_in_progress:
        return {"message": "Embedding is already in progress. Please wait."}

    background_tasks.add_task(rag_service.embed_documents)
    return {"message": "Embedding process started in the background. Please wait."}


@router.post("/query")
def run_query(request: QueryRequest):
    result = rag_service.query(request.question)
    return result
