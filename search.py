
from vector_store import get_embedding_model
from langchain_community.vectorstores import FAISS


# Step 1: Load existing FAISS database
def load_vector_store():
    embeddings = get_embedding_model()

    vector_store = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_store


# Step 2: Search relevant document chunks
def search_documents(
    vector_store,
    question: str,
    top_k: int = 3
):
    results = vector_store.similarity_search(
        query=question,
        k=top_k
    )

    return results
