from dotenv import load_dotenv
load_dotenv()

import tempfile
import os
from pypdf import PdfReader, PdfWriter
from haystack import Document
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.google_genai import (
    GoogleGenAIMultimodalDocumentEmbedder,
    GoogleGenAITextEmbedder,
)
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

PDF_PAGE_LIMIT = 6

def split_pdf_into_chunks(pdf_path: str, chunk_size: int = PDF_PAGE_LIMIT) -> list[tuple[str, str]]:
    """Returns list of (tmp_file_path, extracted_text) tuples."""
    reader = PdfReader(pdf_path)
    chunks = []
    for start in range(0, len(reader.pages), chunk_size):
        pages = reader.pages[start:start + chunk_size]

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


# ── Indexing ──────────────────────────────────────────────────────────────────

source_files = [
    "documents/1706.03762v7.pdf",
    "documents/2205.13147v4.pdf",
    "documents/nested.pdf",
    "documents/semantic.pdf",
]

docs = []
chunk_paths = []

for file_path in source_files:
    chunks = split_pdf_into_chunks(file_path)
    for i, (chunk_path, chunk_text) in enumerate(chunks):
        chunk_paths.append(chunk_path)
        docs.append(Document(
            content=chunk_text,
            meta={
                "file_path": chunk_path,
                "source_file": file_path,
                "chunk_index": i,
            }
        ))

print(f"Indexing: {len(source_files)} PDF → {len(docs)} chunk...")

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

doc_embedder = GoogleGenAIMultimodalDocumentEmbedder(
    model="gemini-embedding-2-preview",
    batch_size=1,
    config={"task_type": "RETRIEVAL_DOCUMENT", "output_dimensionality": 768}
)
docs_with_embeddings = doc_embedder.run(docs)
document_store.write_documents(docs_with_embeddings["documents"])

for path in chunk_paths:
    os.unlink(path)

print(f"{document_store.count_documents()} chunk indexlendi. Chat'e hazır!\n")


# ── RAG Components ────────────────────────────────────────────────────────────

text_embedder = GoogleGenAITextEmbedder(
    model="gemini-embedding-2-preview",
    config={"task_type": "RETRIEVAL_QUERY", "output_dimensionality": 768}
)
retriever = InMemoryEmbeddingRetriever(document_store=document_store, top_k=4)
llm = GoogleGenAIChatGenerator(model="gemini-3.1-flash-lite-preview")


def ask(query: str) -> str:
    query_embedding = text_embedder.run(text=query)["embedding"]
    docs = retriever.run(query_embedding=query_embedding)["documents"]

    context = "\n\n".join(
        f"[{d.meta['source_file']} - chunk {d.meta['chunk_index']}]\n{d.content or ''}"
        for d in docs
    )
    prompt = (
        "Aşağıdaki döküman parçalarını kullanarak soruyu yanıtla.\n"
        "Eğer cevap dökümanlardan çıkarılamıyorsa bunu açıkça belirt.\n\n"
        f"Dökümanlar:\n{context}\n\n"
        f"Soru: {query}"
    )
    messages = [ChatMessage.from_user(prompt)]
    return llm.run(messages=messages)["replies"][0].text


# ── Chat Loop ─────────────────────────────────────────────────────────────────

print("Dökümanlarla sohbet et. Çıkmak için 'q' veya 'quit' yaz.\n")

while True:
    query = input("Sen: ").strip()
    if not query:
        continue
    if query.lower() in ("q", "quit", "exit"):
        print("Çıkılıyor.")
        break

    print(f"\nAsistan: {ask(query)}\n")
