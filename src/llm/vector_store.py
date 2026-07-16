from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.llm.knowledge_base import KNOWLEDGE_BASE_DOCUMENTS

_vectorizer = None
_doc_vectors = None
_documents = None


def _get_index():
    global _vectorizer, _doc_vectors, _documents
    if _vectorizer is None:
        _documents = [doc["content"] for doc in KNOWLEDGE_BASE_DOCUMENTS]
        _vectorizer = TfidfVectorizer(stop_words="english")
        _doc_vectors = _vectorizer.fit_transform(_documents)
    return _vectorizer, _doc_vectors, _documents


def build_knowledge_base():
    """
    Builds a lightweight TF-IDF index over our knowledge base documents.
    Replaces the previous ChromaDB + downloaded embedding model approach,
    which was too memory-heavy for free-tier hosting (512MB RAM limit).
    """
    _get_index()
    print(f"Knowledge base built with {len(KNOWLEDGE_BASE_DOCUMENTS)} documents (TF-IDF index).")


def retrieve_relevant_context(query, n_results=2):
    """
    Given a query string, retrieves the most relevant documents from our
    knowledge base using TF-IDF + cosine similarity.
    """
    vectorizer, doc_vectors, documents = _get_index()
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, doc_vectors)[0]
    top_indices = similarities.argsort()[::-1][:n_results]
    return [documents[i] for i in top_indices]


if __name__ == "__main__":
    build_knowledge_base()
    test_query = "user had multiple failed login attempts in a short time"
    retrieved = retrieve_relevant_context(test_query)
    print(f"\nQuery: {test_query}")
    print("\nRetrieved context:")
    for i, doc in enumerate(retrieved, 1):
        print(f"\n[{i}] {doc[:200]}...")