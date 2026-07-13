import chromadb
from src.llm.knowledge_base import KNOWLEDGE_BASE_DOCUMENTS

# Create a persistent ChromaDB client - "persistent" means data is saved to disk,
# not lost when the program restarts (as opposed to an in-memory-only database)
_client = chromadb.PersistentClient(path="data/vector_db")

# get_or_create_collection: a "collection" in ChromaDB is like a table in a normal database -
# a named group of related documents. This line creates it if it doesn't exist yet,
# or reuses it if we've already built it before.
_collection = _client.get_or_create_collection(name="soc_knowledge_base")


def build_knowledge_base():
    """
    Loads our knowledge base documents into ChromaDB, converting each into an embedding
    automatically (ChromaDB handles the embedding model internally by default).
    Only needs to be run once (or whenever the knowledge base content changes).
    """
    ids = [doc["id"] for doc in KNOWLEDGE_BASE_DOCUMENTS]
    documents = [doc["content"] for doc in KNOWLEDGE_BASE_DOCUMENTS]

    _collection.upsert(
        ids=ids,
        documents=documents
    )
    print(f"Knowledge base built with {len(documents)} documents.")


def retrieve_relevant_context(query, n_results=2):
    """
    Given a query string, retrieves the most semantically similar documents
    from our knowledge base.

    Input:
        query (string) - the question/context to search for
        n_results (int) - how many top matching documents to retrieve
    Output: a list of matching document text strings
    """
    results = _collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0]


if __name__ == "__main__":
    build_knowledge_base()

    # Quick manual test - see what gets retrieved for a sample query
    test_query = "user had multiple failed login attempts in a short time"
    retrieved = retrieve_relevant_context(test_query)

    print(f"\nQuery: {test_query}")
    print("\nRetrieved context:")
    for i, doc in enumerate(retrieved, 1):
        print(f"\n[{i}] {doc[:200]}...")