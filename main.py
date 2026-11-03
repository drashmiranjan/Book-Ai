
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import ChatRequest, ChatResponse
from search import load_vector_store
from rag import get_llm, generate_answer

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting KnowledgeMind AI...")

    app.state.vector_store = load_vector_store()
    app.state.llm = get_llm()

    print("KnowledgeMind AI started successfully!")

    yield

    print("Shutting down KnowledgeMind AI...")


app = FastAPI(
    title="KnowledgeMind AI",
    description="AI-powered document knowledge assistant using RAG",
    version="1.0.0",
    lifespan=lifespan
)



@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "KnowledgeMind AI"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        vector_store = app.state.vector_store
        llm = app.state.llm

        answer = generate_answer(
            question=request.question,
            vector_store=vector_store,
            llm=llm
        )

        return ChatResponse(
            question=request.question,
            answer=answer
        )

    except Exception as e:
        print(f"Chat error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer. Please try again later."
        )

