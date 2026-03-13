from dotenv import load_dotenv
from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.google_genai import (
    GoogleGenAIDocumentEmbedder,
    GoogleGenAITextEmbedder,
    GoogleGenAIMultimodalDocumentEmbedder,
)
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from pypdf import PdfReader
import time

# Load env vars
load_dotenv()


def create_and_embed_text() -> InMemoryDocumentStore:
    """Creates a document store, adds docs and embeds them using GenAI."""
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

    docs = [
        Document(
            content="The capybara is the largest rodent in the world and is native to South America, where it lives near rivers, lakes, and wetlands. It is highly social and often seen relaxing in groups, spending much of its time swimming or soaking in water. Capybaras communicate through whistles, barks, and purr-like sounds."
        ),
        Document(
            content="Dogs are domesticated mammals known for their loyalty, intelligence, and strong bond with humans. They have been bred for thousands of years for roles such as companionship, hunting, guarding, and assisting people with various tasks. Different breeds vary widely in size, temperament, and abilities."
        ),
        Document(
            content="The tiger is the largest species of big cat and is recognized by its distinctive orange coat with black stripes. It is a powerful solitary predator that inhabits forests, grasslands, and wetlands across parts of Asia. Tigers are excellent swimmers and rely on stealth and strength to hunt prey."
        ),
        Document(
            content="The giraffe is the tallest land animal on Earth, easily identified by its long neck and distinctive spotted coat. It uses its height to reach leaves high in acacia trees and roams the savannas and open woodlands of Africa. Despite its long neck, a giraffe has the same number of neck vertebrae as most mammals."
        ),
        Document(
            content="Elephants are the largest land animals and are known for their intelligence, strong family bonds, and remarkable memory. They use their trunks for breathing, grasping objects, and communication. Elephants live in complex social groups led by a matriarch."
        ),
        Document(
            content="Penguins are flightless birds that live primarily in the Southern Hemisphere, especially in Antarctica. They are excellent swimmers, using their flipper-like wings to move through the water while hunting fish, squid, and krill."
        ),
        Document(
            content="Dolphins are highly intelligent marine mammals known for their playful behavior and complex communication. They live in social groups called pods and use echolocation to navigate and locate prey in the ocean."
        ),
        Document(
            content="Owls are nocturnal birds of prey with excellent night vision and silent flight. They hunt small mammals, insects, and other birds, relying on their sharp talons and keen hearing to detect prey in darkness."
        ),
        Document(
            content="Red pandas are small mammals native to the eastern Himalayas and southwestern China. They have reddish-brown fur, bushy tails, and spend most of their time in trees. Their diet mainly consists of bamboo, though they may also eat fruits and insects."
        ),
        Document(
            content="Kangaroos are large marsupials native to Australia and are famous for their powerful hind legs, large feet, and strong tails that help them balance while hopping. Female kangaroos carry and nurture their young, called joeys, in a pouch. They typically live in open grasslands and forests and often move in groups called mobs."
        ),
    ]

    doc_embedder = GoogleGenAIDocumentEmbedder(
        model="gemini-embedding-2-preview",
        batch_size=5,
        config={
            "task_type": "RETRIEVAL_DOCUMENT",
            "output_dimensionality": 768,  # flexible embedding sizes using MRL
        },
    )
    docs_with_embeddings = doc_embedder.run(docs)
    document_store.write_documents(docs_with_embeddings["documents"])

    return document_store


def embed_documents() -> InMemoryDocumentStore:
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

    paper_paths = [
        "./documents/1706.03762v7.pdf",
        # "./documents/2205.13147v4.pdf",
        # "./documents/Nested Learning.pdf",
        "./documents/Semantic_Information_Extraction_and_Multi-Agent_Communication_Optimization_Based_on_Generative_Pre-Trained_Transformer.pdf",
    ]

    docs = []
    for paper_path in paper_paths:
        reader = PdfReader(paper_path)
        num_pages = len(reader.pages)
        for i in range(1, num_pages + 1):
            docs.append(
                Document(
                    meta={
                        "file_path": paper_path,
                        "page_number": i,
                    }
                )
            )

    doc_embedder = GoogleGenAIMultimodalDocumentEmbedder(
        model="gemini-embedding-2-preview",
        batch_size=5,
        config={
            "task_type": "RETRIEVAL_DOCUMENT",
            "output_dimensionality": 768,  # flexible embedding sizes using MRL
        },
    )

    # Send requests in 1 min delay
    for i in range(0, len(docs), 5):
        docs_with_embeddings = doc_embedder.run(docs[i : i + 5])
        document_store.write_documents(docs_with_embeddings["documents"])
        print(
            f"Embeddings for documents {i} to {i + 5} have been written to the document store."
        )
        time.sleep(60)

    return document_store


def retrieve_query(
    document_store: InMemoryDocumentStore,
    query: str = "animal that communicates with whistles and barks",
):
    """Embeds the query and retrieves the most relevant documents."""
    embedding_retriever = InMemoryEmbeddingRetriever(document_store=document_store)

    text_embedder = GoogleGenAITextEmbedder(
        model="gemini-embedding-2-preview",
        config={
            "task_type": "RETRIEVAL_QUERY",
            "output_dimensionality": 768,  # flexible embedding sizes using MRL
        },
    )
    query_embedding = text_embedder.run(query)["embedding"]

    result = embedding_retriever.run(query_embedding=query_embedding, top_k=2)

    for doc in result["documents"]:
        print(doc.meta)
        print(doc.content)
        print(doc.score)
        print("-" * 10)

    return result


def retrieve_documents(
    document_store: InMemoryDocumentStore,
    query: str = "What is Nested Learning?",
):
    """Embeds the query and retrieves the most relevant documents."""
    embedding_retriever = InMemoryEmbeddingRetriever(document_store=document_store)

    text_embedder = GoogleGenAITextEmbedder(
        model="gemini-embedding-2-preview",
        config={
            "task_type": "RETRIEVAL_DOCUMENT",
            "output_dimensionality": 768,  # flexible embedding sizes using MRL
        },
    )
    query_embedding = text_embedder.run(query)["embedding"]

    result = embedding_retriever.run(query_embedding=query_embedding, top_k=2)[
        "documents"
    ]

    for doc in result:
        print(doc.meta)
        print(doc.content)
        print(doc.score)
        print("-" * 10)

    return result


def main():
    store = embed_documents()
    print(f"Successfully embedded and stored {store.count_documents()} documents.")
    print("=" * 40)
    print("Executing retrieval query:")
    retrieve_query(store)
    print("=" * 40)
    print("Executing retrieval documents:")
    retrieve_documents(store, "What is Semantic Information Extraction?")


if __name__ == "__main__":
    main()
