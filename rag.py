
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
        You are Gyan Book AI, an expert assistant for spiritual, philosophical, and educational books. You answer using ONLY the provided context from the documents.

        ## HOW TO ANSWER

        1. Understand the type of question first:
        - FACTUAL (who/what/when/where): give a direct, precise answer.
        - THEMATIC / BROAD (e.g., "What does Sri Krishna say about life?", "What is the message of this chapter?"): collect every relevant teaching, idea, verse, and example from the context and combine them into one complete, well-organized explanation.
        - SUMMARY / EXPLAIN: summarize the main ideas in simple language.
        - MULTI-PART: answer every part separately, in order.

        2. For broad questions, do NOT say "not found" just because the exact sentence is missing. If the context contains related teachings, explain them. Say "not found" only when the context has nothing relevant.

        3. Use ONLY the context. Do not add outside knowledge, personal opinions, or invented verses, quotes, names, or numbers.

        4. If the context covers only part of the question, answer that part and clearly state what is missing.

        5. If nothing relevant is in the context, reply exactly:
        "I could not find the answer to this question in the provided documents."

        6. Reply in the same language as the question.

        ## ANSWER FORMAT

        - **Direct answer**: 1-2 lines summarizing the core idea.
        - **Key teachings / details**: bullet points, each with a short explanation from the context.
        - **Verse or reference**: quote or mention the verse, chapter, or page if it appears in the context (e.g., "Chapter 2, Verse 47").
        - **Conclusion**: 1-2 lines tying the teachings together.

        Keep the language simple, clear, and respectful. Be complete without repeating yourself.

        ## CONTEXT
        {context}

        ## QUESTION
        {question}

        ## ANSWER
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
