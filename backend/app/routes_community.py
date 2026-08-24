from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import get_db
from .dependencies import CurrentUser
from .models import Comment, CommentStatus, Favorite, Note, NoteStatus
from .schemas import CommentRead, NoteList, NoteRead, PublicCommentCreate

router = APIRouter(tags=["community"])


def public_note(db: Session, note_id: int) -> Note:
    note = db.scalar(select(Note).where(Note.id == note_id, Note.is_public.is_(True)))
    if not note:
        raise HTTPException(status_code=404, detail="Public note not found")
    return note


@router.get("/api/public/notes/{note_id}", response_model=NoteRead)
def get_public_note(note_id: int, db: Session = Depends(get_db)) -> Note:
    note = public_note(db, note_id)
    note.views += 1
    db.commit()
    db.refresh(note)
    return note


@router.post("/api/public/notes/{note_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_public_comment(note_id: int, payload: PublicCommentCreate, db: Session = Depends(get_db)) -> Comment:
    public_note(db, note_id)
    if any(word in payload.content.lower() for word in ("诈骗", "spam", "viagra")):
        raise HTTPException(status_code=422, detail="Comment contains blocked content")
    comment = Comment(note_id=note_id, nickname=payload.nickname.strip(), email=payload.email, content=payload.content.strip())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.post("/api/notes/{note_id}/favorite", status_code=status.HTTP_201_CREATED)
def add_favorite(note_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> dict[str, bool]:
    note = db.scalar(select(Note).where(Note.id == note_id, Note.user_id == user.id))
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    existing = db.scalar(select(Favorite).where(Favorite.note_id == note_id, Favorite.user_id == user.id))
    if not existing:
        db.add(Favorite(note_id=note_id, user_id=user.id))
        db.commit()
    return {"is_favorite": True}


@router.delete("/api/notes/{note_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(note_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> None:
    existing = db.scalar(select(Favorite).where(Favorite.note_id == note_id, Favorite.user_id == user.id))
    if existing:
        db.delete(existing)
        db.commit()


@router.get("/api/favorites", response_model=list[NoteRead])
def list_favorites(user: CurrentUser, db: Session = Depends(get_db)) -> list[Note]:
    return list(db.scalars(select(Note).join(Favorite, Favorite.note_id == Note.id).where(Favorite.user_id == user.id).order_by(Favorite.created_time.desc())).unique())
