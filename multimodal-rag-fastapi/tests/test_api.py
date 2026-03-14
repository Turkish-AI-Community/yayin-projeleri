import os

os.environ["GOOGLE_API_KEY"] = "dummy_api_key_for_testing"

from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_embed_files():
    with patch("app.services.rag_service.RAGService.embed_documents", return_value=2):
        response = client.post("/api/embed")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Successfully embedded 2 document components."
        }


def test_run_query():
    mock_response = {
        "answer": "This is a mocked answer.",
        "documents": [{"file_path": "dummy.pdf", "page_number": 1}],
    }
    with patch("app.services.rag_service.RAGService.query", return_value=mock_response):
        response = client.post("/api/query", json={"question": "What is life?"})
        assert response.status_code == 200
        assert response.json() == mock_response
