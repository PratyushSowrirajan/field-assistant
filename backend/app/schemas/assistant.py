import uuid

from pydantic import BaseModel


class ChatTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class AssistantAskRequest(BaseModel):
    question: str
    field_id: uuid.UUID | None = None
    history: list[ChatTurn] = []


class AssistantAskResponse(BaseModel):
    answer: str
    sources: list[str]
