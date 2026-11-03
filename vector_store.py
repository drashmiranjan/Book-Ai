from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from pdf_loader import load_all_pdfs
from chunker import create_chunks


# Step 1: Initialize embedding model
def get_embedding_model():
    embeddings = HuggingFaceEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings

# Step2: Initialize  embedding chunks
def get_document_chunks():

    documents = load_all_pdfs()
    print("\n creating docs chunks...")

    chunks = create_chunks(documents)

    print("total Documents", len(documents))
    print("Total chunks"), len(chunks)

    return chunks

# Step3: Build the FASSI Vector Database
def build_vector_store():
    print("\nLoadding embedding model..")
    embeddings = get_embedding_model()

    print("\n Loadding document chunks..")
    chunks = get_document_chunks()

    if not chunks:
        raise ValueError("No document chunks found!")
    
    # creating vector database and saving in FASSI vector database
    print("\nSaving FASSI index...")
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    print("\nSaving FASSI index...")

    vector_store.save_local("faiss_index")
    print("\nFASSI vector database created sucessfully")
    return vector_store

    
# Step 4: Execute only when running this file directly
if __name__ == "__main__":
    build_vector_store()