from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .ai_service import answer_question, index_note
from .db import get_db
from .dependencies import CurrentUser
from .models import Note
from .schemas import AIAnswer, AIQuestion, IndexResult

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/notes/{note_id}/index", response_model=IndexResult)
def index(note_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> IndexResult:
    note = db.scalar(select(Note).where(Note.id == note_id, Note.user_id == user.id))
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return IndexResult(note_id=note.id, chunks=index_note(db, note))


@router.post("/ask", response_model=AIAnswer)
def ask(payload: AIQuestion, user: CurrentUser, db: Session = Depends(get_db)) -> AIAnswer:
    answer, matches = answer_question(db, user.id, payload.question)
    return AIAnswer(
        answer=answer,
        sources=[{"note_id": note.id, "title": note.title, "excerpt": excerpt[:180], "score": round(score, 4)} for note, excerpt, score in matches],
    )
