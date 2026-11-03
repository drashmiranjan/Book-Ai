
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500,
        description="Question asked by the user"
    )


class Source(BaseModel):
    book: str
    page: int | None = None


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source] = Field(default_factory=list)
