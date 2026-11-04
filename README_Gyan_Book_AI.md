# 📚 Gyan Book AI

> **Ask questions. Explore books. Learn smarter.**\
> Gyan Book AI is an AI-powered book assistant that uses
> Retrieval-Augmented Generation (RAG) to answer questions from PDF
> books using retrieved document context.

**LangChain · FastAPI · FAISS · Hugging Face · RAG**

------------------------------------------------------------------------

## ✨ What is Gyan Book AI?

Gyan Book AI was inspired by a personal problem: my reading habit was
gradually decreasing, and searching through hundreds of pages to find
one specific answer could be time-consuming.

The goal is to make books easier to interact with. Instead of manually
searching a document, users can ask a question and receive an answer
grounded in relevant passages retrieved from the book.

### Core capabilities

-   📄 Load and process PDF books
-   ✂️ Split extracted text into manageable chunks
-   🧠 Generate text embeddings with `all-MiniLM-L6-v2`
-   🔎 Retrieve semantically relevant passages using FAISS
-   💬 Generate context-aware answers with an LLM through a RAG pipeline
-   ⚡ Serve the chat workflow through a FastAPI API
-   ♻️ Reuse initialized vector-store and LLM resources during
    application runtime

------------------------------------------------------------------------

## 🧰 Tech Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Language                Python                  Core application logic

  API                     FastAPI                 Backend endpoints

  API server              Uvicorn                 Run the FastAPI
                                                  application

  Orchestration           LangChain               Connect retrieval and
                                                  LLM components

  PDF processing          PDF loader              Extract text from PDF
                                                  documents

  Text splitting          LangChain text splitter Divide documents into
                                                  chunks

  Embeddings              Hugging Face            Convert text into
                          `all-MiniLM-L6-v2`      vectors

  Vector store            FAISS                   Similarity search over
                                                  embeddings

  LLM                     Configured provider via Generate answers from
                          LangChain               retrieved context

  Frontend                Streamlit               User-facing chat
                                                  interface

  Version control         Git & GitHub            Source control
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🧭 How It Works

### RAG workflow

``` mermaid
flowchart TD
    A([📚 PDF Books]) --> B[PDF Loader]
    B --> C[Extract Text]
    C --> D[Text Splitter]
    D --> E[Document Chunks]
    E --> F[Hugging Face Embeddings]
    F --> G[(FAISS Vector Store)]
    G --> H[Persist Index]

    I([💬 User Question]) --> J[Question Embedding]
    J --> K[FAISS Similarity Search]
    G --> K
    K --> L[Relevant Chunks]
    L --> M[Build Context + Prompt]
    I --> M
    M --> N[LLM]
    N --> O([📝 Generated Answer])
```

### Request flow

``` mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant RAG as RAG Pipeline
    participant FAISS as FAISS
    participant LLM as Language Model

    User->>UI: Ask a question
    UI->>API: POST /chat
    API->>RAG: Question + initialized components
    RAG->>FAISS: Retrieve relevant chunks
    FAISS-->>RAG: Context passages
    RAG->>LLM: Prompt + retrieved context
    LLM-->>RAG: Generated answer
    RAG-->>API: Answer
    API-->>UI: Chat response
    UI-->>User: Display answer
```

------------------------------------------------------------------------

## 🗂️ Project Structure

``` text
BookAi/
├── books/                  # Local PDF books (keep out of Git)
├── faiss_index/            # Persisted FAISS index files
│   ├── index.faiss
│   └── index.pkl
├── main.py                 # FastAPI application and chat endpoint
├── pdf_loader.py           # PDF loading and text extraction
├── chunker.py              # Document chunking
├── vector_store.py          # Embedding model + FAISS creation/loading
├── search.py                # Similarity retrieval
├── rag.py                   # Context, prompt, and answer generation
├── requirements-backend.txt # Backend dependencies
├── streamlit_app.py         # Streamlit frontend (if present)
├── .env.example             # Example environment configuration
├── .gitignore
└── README.md
```

> File names above describe the project modules discussed during
> development. Adjust this tree if your current repository differs.

------------------------------------------------------------------------

## ⚙️ Local Setup

### 1. Clone the repository

``` bash
git clone https://github.com/drashmiranjan/Book-Ai.git
cd Book-Ai
```

### 2. Create a virtual environment

**Windows PowerShell**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Git Bash**

``` bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements-backend.txt
```

### 4. Configure environment variables

Create a `.env` file from `.env.example` and add the API key for the LLM
provider configured in the project.

``` env
# Example only — use the variable names required by your code
LLM_API_KEY=your_api_key_here
```

**Never commit `.env` or real API keys.**

### 5. Prepare PDF books

Place your PDF files in the local `books/` directory. Keep copyrighted
or large source PDFs out of the Git repository unless you have
permission to distribute them.

### 6. Build the FAISS index

Run the vector-store module using the command supported by your
repository:

``` bash
python vector_store.py
```

This loads the PDFs, extracts text, creates chunks, generates
embeddings, and saves the FAISS index.

### 7. Start the FastAPI backend

``` bash
uvicorn main:app --reload
```

Open the interactive API documentation:

-   `http://127.0.0.1:8000/docs`

### 8. Start the Streamlit frontend

In a separate terminal:

``` bash
streamlit run streamlit_app.py
```

> Confirm the frontend API URL matches the address where FastAPI is
> running.

------------------------------------------------------------------------

## 🔌 API

### `POST /chat`

Accepts a user question and returns an answer generated by the RAG
pipeline.

**Example request**

``` json
{
  "question": "What is the central message of the Bhagavad Gita?"
}
```

**Example response shape**

``` json
{
  "question": "What is the central message of the Bhagavad Gita?",
  "answer": "Answer generated from the retrieved book context."
}
```

> The exact request and response fields depend on the Pydantic models in
> `main.py`. Check `/docs` for the live schema.

------------------------------------------------------------------------

## 🧠 Key Engineering Decisions

-   **Chunking instead of whole-book prompts:** keeps retrieval focused
    and context manageable.
-   **Semantic retrieval instead of keyword-only search:** can find
    passages related in meaning, even when wording differs.
-   **FAISS persistence:** avoids rebuilding the vector index for every
    application start.
-   **Application lifespan initialization:** loads the vector store and
    LLM once and stores them in `app.state`.
-   **Resource reuse in `/chat`:** avoids repeatedly initializing heavy
    components for each request.
-   **Modular code:** separates PDF loading, chunking, indexing,
    retrieval, RAG, and API concerns.

------------------------------------------------------------------------

## 🧩 Challenges & Lessons Learned

  -----------------------------------------------------------------------
  Challenge                           What I learned / how I addressed it
  ----------------------------------- -----------------------------------
  HTTP 500 from response validation   Align the returned payload with the
                                      Pydantic response model and its
                                      required fields.

  Repeated model/vector-store         Initialize heavy resources at
  initialization                      startup and reuse them through
                                      `app.state`.

  Dependency conflict during ONNX     Revert incompatible extras and
  experimentation                     restore the known embedding
                                      configuration.

  Unintended PDF staging with         Inspect `git status` and unstage
  `git add .`                         local books before committing.

  Frontend/backend development reload Keep development watch paths and
  interference                        processes scoped to the relevant
                                      application.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🔭 Roadmap

-   [ ] Improve prompt design and answer grounding
-   [ ] Improve retrieval quality and tune chunking / search parameters
-   [ ] Add source citations and page references to answers
-   [ ] Add conversational memory
-   [ ] Add book selection and library management
-   [ ] Add personalized reading recommendations
-   [ ] Add evaluation tests for retrieval and answer quality
-   [ ] Improve UI/UX and loading/error states
-   [ ] Add observability and structured logging

------------------------------------------------------------------------

## 🎯 Learning Outcomes

Through Gyan Book AI, I practiced and connected:

-   PDF ingestion and text processing
-   Chunking strategies
-   Embeddings and vector representations
-   Vector databases and similarity search
-   Retrieval-Augmented Generation
-   Prompt/context construction
-   FastAPI endpoint design and Pydantic validation
-   Application lifespan and resource reuse
-   Dependency management and debugging
-   Git workflow and repository hygiene

------------------------------------------------------------------------

## 💡 Why I Built It

Gyan Book AI began with a personal challenge: I wanted to make it easier
to engage with books and find useful information without losing the
value of their content.

The project helped me move from studying GenAI concepts individually to
building an application that combines them into a practical workflow.

I'm continuing to improve it with better retrieval, grounding, and user
experience.

------------------------------------------------------------------------

## 🤝 Feedback & Contributions

Suggestions, feedback, and ideas are welcome. If you have an idea that
could make Gyan Book AI more useful, feel free to open an issue or share
your thoughts.

------------------------------------------------------------------------

## 👨‍💻 Author

**Rashmi Ranjan Das**

-   GitHub: [@drashmiranjan](https://github.com/drashmiranjan)
-   Portfolio:
    [drashmiranjan.vercel.app](https://drashmiranjan.vercel.app/)

------------------------------------------------------------------------

```{=html}
<p align="center">
```
`<strong>`{=html}Built with curiosity, debugging, and a love for
learning. 📚🤖`</strong>`{=html}
```{=html}
</p>
```
