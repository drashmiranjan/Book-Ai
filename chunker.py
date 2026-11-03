from langchain_text_splitters import RecursiveCharacterTextSplitter

from pdf_loader import load_all_pdfs

def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    print("Chunks created:", len(chunks))

    return(chunks)

























if __name__ == "__main__":

    documents = load_all_pdfs()

    print("\nCreating chunks...")

    chunks = create_chunks(documents)

    print("\n========== CHUNKING SUMMARY ==========")
    print("Total pages:", len(documents))
    print("Total chunks:", len(chunks))

    if chunks:

        print("\nFirst chunk:")
        print(chunks[0].page_content[:500])

        print("\nFirst chunk metadata:")
        print(chunks[0].metadata)

        print("\nFirst chunk length:")
        print(len(chunks[0].page_content))