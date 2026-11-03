
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from search import load_vector_store, search_documents

load_dotenv()


# Step 1: Initialize Groq LLM
def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=1024,
    )


# Step 2: Generate answer using retrieved context
def generate_answer(
    question: str,
    vector_store,
    llm
):
    # Retrieve relevant document chunks
    documents = search_documents(
        vector_store=vector_store,
        question=question,
        top_k=3
    )

    # Create context from retrieved chunks
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # Construct prompt
    prompt = f"""
You are KnowledgeMind AI, a document knowledge assistant.

Answer using ONLY the provided context.
If the answer is unavailable in the context,
say that you could not find the answer in the documents.

Context:
{context}

Question:
{question}

Answer:
"""

    # Generate response
    response = llm.invoke(prompt)

    return response.content


# Step 3: Run terminal chatbot
if __name__ == "__main__":
    vector_store = load_vector_store()
    llm = get_llm()

    print("\n========== KNOWLEDGEMIND AI ==========")
    print("Ask questions about your books.")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        answer = generate_answer(
            question=question,
            vector_store=vector_store,
            llm=llm
        )

        print("\nAI:", answer)
