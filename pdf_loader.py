from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


# PDF directory
BOOKS_DIR = Path("books")

def load_all_pdfs():
    documents = []

    # Find all the PDf files
    pdf_files = list(BOOKS_DIR.glob("*.pdf"))  # here *.pdf means select all the files

    print(pdf_files)

    if not pdf_files:
        print("No Pdf founds....")
        return documents
    print(f"Found {len(pdf_files)} PDF files")

    #Process each PDF
    for pdf_path in pdf_files:
        print(f"\n loading: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        documents.extend(pages)
        print(f"pages extracted {len(pages)}")
    return documents





































if __name__ == "__main__":

    docs = load_all_pdfs()

    print("\nTotal pages:", len(docs))

    if docs:

        print("\nFirst page content:")
        print(docs[0].page_content[:500])

        print("\nMetadata:")
        print(docs[0].metadata)
