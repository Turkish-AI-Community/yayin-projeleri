from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from pydantic import BaseModel
from app.services.rag_service import rag_service
from pathlib import Path
import shutil

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".mp4", ".mov", ".mp3", ".wav", ".m4a"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return {"error": f"File type {file_ext} not supported. Supported types: {', '.join(allowed_extensions)}"}, 400
    
    upload_dir = Path("./documents")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"message": f"Successfully uploaded {file.filename}", "file_path": str(file_path)}


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


@router.get("/status")
def get_status():
    return {"embedding_in_progress": rag_service.embedding_in_progress}
