from unittest.mock import patch, mock_open
from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from main import create_and_embed_text, retrieve_documents, embed_documents


def test_create_and_embed_text():
    """Test standard execution of document embedding using mocked GenAI."""
    mock_embeddings = {
        "documents": [Document(content="Test content", embedding=[0.1] * 768)]
    }

    with patch("main.GoogleGenAIDocumentEmbedder") as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.run.return_value = mock_embeddings

        document_store = create_and_embed_text()

        # Document store should contain the embedded documents
        stored_docs = document_store.filter_documents()
        assert len(stored_docs) > 0

        # Checking that our mock was indeed called
        mock_instance.run.assert_called_once()

        # Verifying dimensions matching the config
        assert stored_docs[0].embedding == [0.1] * 768


def test_retrieve_documents():
    """Test standard execution of document retrieval using mocked GenAI text embedder."""
    mock_query_embedding = {"embedding": [0.1] * 768}

    # Create minimal doc store
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
    test_doc = Document(content="Test animal content", embedding=[0.1] * 768, score=1.0)
    document_store.write_documents([test_doc])

    with patch("main.GoogleGenAITextEmbedder") as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.run.return_value = mock_query_embedding

        result = retrieve_documents(document_store, query="test query")

        # Checking that our mock was indeed called
        mock_instance.run.assert_called_once_with("test query")

        # Check retrieval was successful
        assert len(result) > 0
        assert result[0].content == "Test animal content"


def test_embed_documents():
    """Test execution of PDF conversion and embedding using mocked parts."""
    mock_embeddings = {
        "documents": [Document(meta={"file_path": "dummy1.pdf"}, embedding=[0.2] * 768)]
    }

    with (
        patch("main.PdfReader") as mock_pdf_reader,
        patch("main.GoogleGenAIMultimodalDocumentEmbedder") as mock_embedder_class,
    ):
        mock_instance = mock_embedder_class.return_value
        mock_instance.run.return_value = mock_embeddings

        # Ensure mocked reader returns a single page to iterate gracefully
        mock_pdf_reader.return_value.pages = [1]

        document_store = embed_documents()
        stored_docs = document_store.filter_documents()

        assert len(stored_docs) > 0
        assert stored_docs[0].embedding == [0.2] * 768
        mock_instance.run.assert_called_once()
