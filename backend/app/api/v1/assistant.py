import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models.user import Farmer
from app.schemas.assistant import AssistantAskRequest, AssistantAskResponse
from app.services import assistant
from app.services.llm_client import LLMError

router = APIRouter(prefix="/assistant", tags=["assistant"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AssistantAskResponse)
async def ask_assistant(
    payload: AssistantAskRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question can't be empty")
    if len(question) > 500:
        raise HTTPException(status_code=400, detail="Keep the question under 500 characters")

    try:
        answer, sources = await assistant.ask(
            db,
            farmer,
            question,
            payload.field_id,
            [t.model_dump() for t in payload.history],
        )
    except LLMError as exc:
        logger.warning("assistant: LLM call failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The assistant isn't available right now. Please try again in a moment.",
        )

    return AssistantAskResponse(answer=answer, sources=sources)
