import os

os.environ["GOOGLE_API_KEY"] = "dummy_api_key_for_testing"

from unittest.mock import patch, MagicMock
from haystack import Document
from haystack.dataclasses import ChatMessage

# Patch components to prevent API keys validation errors on import or run
with (
    patch("app.services.rag_service.GoogleGenAIChatGenerator"),
    patch("app.services.rag_service.GoogleGenAITextEmbedder"),
    patch("app.services.rag_service.GoogleGenAIMultimodalDocumentEmbedder"),
    patch("app.services.rag_service.InMemoryEmbeddingRetriever"),
):
    from app.services.rag_service import rag_service


def test_query():
    mock_pipeline_result = {
        "llm": {"replies": [ChatMessage.from_assistant("This is a test response.")]},
        "retriever": {
            "documents": [Document(meta={"file_path": "test.pdf", "page_number": 1})]
        },
    }

    with patch.object(rag_service.pipeline, "run", return_value=mock_pipeline_result):
        result = rag_service.query("What is testing?")
        assert result["answer"] == "This is a test response."
        assert len(result["documents"]) == 1
        assert result["documents"][0]["file_path"] == "test.pdf"


def test_embed_documents():
    mock_embeddings = {
        "documents": [Document(meta={"file_path": "dummy1.pdf"}, embedding=[0.2] * 768)]
    }

    with (
        patch("app.services.rag_service.Path.exists", return_value=True),
        patch("app.services.rag_service.PdfReader") as mock_pdf_reader,
        patch("app.services.rag_service.PdfWriter"),
        patch("app.services.rag_service.os.unlink"),
        patch(
            "app.services.rag_service.GoogleGenAIMultimodalDocumentEmbedder"
        ) as mock_embedder_class,
    ):
        mock_instance = mock_embedder_class.return_value
        mock_instance.run.return_value = mock_embeddings

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "dummy text"
        mock_pdf_reader.return_value.pages = [mock_page]

        # Override the paths directly to avoid actually reading
        with patch("app.services.rag_service.time.sleep"):  # disable sleep in test
            count = rag_service.embed_documents()

        assert count > 0
