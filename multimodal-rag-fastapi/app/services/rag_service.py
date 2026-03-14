import time
import os
import tempfile
from app.core.config import settings
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from haystack import Document, Pipeline
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack_integrations.components.retrievers.weaviate import (
    WeaviateEmbeddingRetriever,
)
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack.utils.auth import Secret
from haystack_integrations.components.embedders.google_genai import (
    GoogleGenAITextEmbedder,
    GoogleGenAIMultimodalDocumentEmbedder,
)
from haystack_integrations.components.generators.google_genai import (
    GoogleGenAIChatGenerator,
)


class RAGService:
    def __init__(self):
        self.embedding_in_progress = False
        self.document_store = WeaviateDocumentStore(url="http://localhost:8080")
        self._setup_pipeline()

    def _setup_pipeline(self):
        # Retriever
        self.retriever = WeaviateEmbeddingRetriever(document_store=self.document_store)

        # Generator components
        prompt_template = """
        Answer the following question based only on the provided documents.
        If the answer is not in the documents, say "I don't know".
        
        Documents:
        {% for doc in documents %}
            [{{ doc.meta.source_file }} - chunk {{ doc.meta.chunk_index }}]
            {{ doc.content }}
        {% endfor %}
        
        Question: {{ query }}
        """

        # Configure ChatPromptBuilder which outputs List[ChatMessage]
        template = [ChatMessage.from_user(prompt_template)]
        self.prompt_builder = ChatPromptBuilder(
            template=template, required_variables=["query", "documents"]
        )

        # gemini-3.1-flash-lite-preview generating the responses
        api_secret = Secret.from_token(settings.GEMINI_API_KEY)
        self.generator = GoogleGenAIChatGenerator(
            api_key=api_secret, model="gemini-3.1-flash-lite-preview"
        )
        self.text_embedder = GoogleGenAITextEmbedder(
            api_key=api_secret,
            model="gemini-embedding-2-preview",
            config={
                "task_type": "RETRIEVAL_QUERY",
                "output_dimensionality": 768,
            },
        )

        self.pipeline = Pipeline()
        self.pipeline.add_component("text_embedder", self.text_embedder)
        self.pipeline.add_component("retriever", self.retriever)
        self.pipeline.add_component("prompt_builder", self.prompt_builder)
        self.pipeline.add_component("llm", self.generator)

        self.pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        self.pipeline.connect("retriever", "prompt_builder.documents")
        self.pipeline.connect("prompt_builder.prompt", "llm.messages")

    def embed_documents(self):

        self.embedding_in_progress = True
        try:
            paper_paths = [
                "./documents/1706.03762v7.pdf",
                "./documents/2205.13147v4.pdf",
                "./documents/Semantic_Information_Extraction_and_Multi-Agent_Communication_Optimization_Based_on_Generative_Pre-Trained_Transformer.pdf",
                "./documents/Nested Learning.pdf",
            ]

            def split_pdf_into_chunks(pdf_path: str, chunk_size: int = 6):
                reader = PdfReader(pdf_path)
                chunks = []
                for start in range(0, len(reader.pages), chunk_size):
                    pages = reader.pages[start : start + chunk_size]

                    writer = PdfWriter()
                    text_parts = []
                    for page in pages:
                        writer.add_page(page)
                        text_parts.append(page.extract_text() or "")

                    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                    writer.write(tmp)
                    tmp.close()
                    chunks.append((tmp.name, "\n".join(text_parts)))
                return chunks

            docs = []
            chunk_paths = []
            for paper_path in paper_paths:
                if not Path(paper_path).exists():
                    print(f"Skipping missing document: {paper_path}")
                    continue

                existing_docs = self.document_store.filter_documents(
                    filters={
                        "operator": "==",
                        "field": "source_file",
                        "value": paper_path,
                    }
                )
                if len(existing_docs) > 0:
                    print(
                        f"Document {paper_path} already embedded in Weaviate. Skipping..."
                    )
                    continue

                chunks = split_pdf_into_chunks(paper_path)
                for i, (chunk_path, chunk_text) in enumerate(chunks):
                    chunk_paths.append(chunk_path)
                    docs.append(
                        Document(
                            content=chunk_text,
                            meta={
                                "file_path": chunk_path,
                                "source_file": paper_path,
                                "chunk_index": i,
                            },
                        )
                    )

            if len(docs) > 0:
                doc_embedder = GoogleGenAIMultimodalDocumentEmbedder(
                    api_key=Secret.from_token(settings.GEMINI_API_KEY),
                    model="gemini-embedding-2-preview",
                    batch_size=1,
                    config={
                        "task_type": "RETRIEVAL_DOCUMENT",
                        "output_dimensionality": 768,
                    },
                )

                for i in range(0, len(docs), 5):
                    docs_with_embeddings = doc_embedder.run(docs[i : i + 5])
                    self.document_store.write_documents(
                        docs_with_embeddings["documents"]
                    )
                    print(f"Embeddings for documents {i} to {i + 5} have been written.")
                    time.sleep(60)

            for path in chunk_paths:
                try:
                    os.unlink(path)
                except OSError:
                    pass

            return self.document_store.count_documents()
        finally:
            self.embedding_in_progress = False

    def query(self, question: str):
        if self.embedding_in_progress:
            return {
                "answer": "Embedding still working please wait 5 minutes to try again",
                "documents": [],
            }
        result = self.pipeline.run(
            {
                "text_embedder": {"text": question},
                "prompt_builder": {"query": question},
            },
            include_outputs_from={"retriever"},
        )
        return {
            "answer": result["llm"]["replies"][0].text,
            "documents": [
                {"meta": doc.meta, "score": doc.score}
                for doc in result["retriever"]["documents"]
            ],
        }


rag_service = RAGService()
