from app.services.rag_service import rag_service

print(
    "Starting document embedding... (This will take a few minutes due to the 60-second delay per 5 pages for API rate limits)"
)
try:
    count = rag_service.embed_documents()
    print(f"Successfully embedded {count} pages.")

    print("\nQuerying: 'What is Semantic Information Extraction?'")
    result = rag_service.query("What is Semantic Information Extraction?")

    print("\n" + "=" * 40)
    print("ANSWER:")
    print("=" * 40)
    print(result.get("answer", "No answer found."))
    print("=" * 40)
    print("SOURCES:")
    for doc in result.get("documents", []):
        print(f"- {doc.get('file_path')} (Page {doc.get('page_number')})")

except Exception as e:
    print(f"An error occurred: {e}")
