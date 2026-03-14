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
        self.document_store = WeaviateDocumentStore(url=settings.WEAVIATE_URL)
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
            docs_dir = Path("./documents")
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Supported extensions
            exts = {".pdf", ".png", ".jpg", ".jpeg", ".mp4", ".mov", ".mp3", ".wav", ".m4a"}
            all_file_paths = [str(f) for f in docs_dir.iterdir() if f.suffix.lower() in exts]
            
            if not all_file_paths:
                print("No supported documents found in ./documents directory.")
                return 0

            def get_pdf_chunks(pdf_path: str, chunk_size: int = 6):
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
                    chunks.append((tmp.name, f"PDF Subset: {Path(pdf_path).name} (Pages {start+1}-{min(start+chunk_size, len(reader.pages))})\n" + "\n".join(text_parts)))
                return chunks

            docs = []
            temp_paths = []
            
            for file_path in all_file_paths:
                p = Path(file_path)
                suffix = p.suffix.lower()
                
                # Check for existing docs
                try:
                    existing = self.document_store.filter_documents(
                        filters={"operator": "==", "field": "source_file", "value": str(file_path)}
                    )
                    if existing:
                        print(f"Skipping {file_path}, already indexed.")
                        continue
                except Exception:
                    pass

                if suffix == ".pdf":
                    chunks = get_pdf_chunks(str(file_path))
                    for i, (chunk_path, chunk_text) in enumerate(chunks):
                        temp_paths.append(chunk_path)
                        docs.append(Document(
                            content=chunk_text,
                            meta={"file_path": chunk_path, "source_file": str(file_path), "chunk_index": i, "type": "pdf"}
                        ))
                elif suffix in {".png", ".jpg", ".jpeg"}:
                    docs.append(Document(
                        content=f"Image file: {p.name}",
                        meta={"file_path": str(file_path), "source_file": str(file_path), "type": "image"}
                    ))
                elif suffix in {".mp4", ".mov"}:
                    docs.append(Document(
                        content=f"Video file: {p.name}",
                        meta={"file_path": str(file_path), "source_file": str(file_path), "type": "video"}
                    ))
                elif suffix in {".mp3", ".wav", ".m4a"}:
                    docs.append(Document(
                        content=f"Audio file: {p.name}",
                        meta={"file_path": str(file_path), "source_file": str(file_path), "type": "audio"}
                    ))

            if docs:
                doc_embedder = GoogleGenAIMultimodalDocumentEmbedder(
                    api_key=Secret.from_token(settings.GEMINI_API_KEY),
                    model="gemini-embedding-2-preview",
                    batch_size=1,
                    config={"task_type": "RETRIEVAL_DOCUMENT", "output_dimensionality": 768},
                )

                # Process in small batches
                for i in range(0, len(docs), 5):
                    batch = docs[i : i + 5]
                    response = doc_embedder.run(batch)
                    self.document_store.write_documents(response["documents"])
                    print(f"Indexed {len(batch)} items ({i+len(batch)}/{len(docs)})")

            # Cleanup temp files
            for path in temp_paths:
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
