from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .dependencies import CurrentUser
from .models import Note
from .schemas import NoteCreate, NoteList, NoteRead, NoteUpdate
from .services import create_note, search_notes, update_note

router = APIRouter(prefix="/api/notes", tags=["notes"])


def owned_note(db: Session, note_id: int, user_id: int) -> Note:
    note = db.scalar(select(Note).where(Note.id == note_id, Note.user_id == user_id))
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("", response_model=NoteList)
def list_notes(
    user: CurrentUser,
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, max_length=100),
) -> NoteList:
    items, total = search_notes(db, user.id, q)
    return NoteList(items=items, total=total)


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create(payload: NoteCreate, user: CurrentUser, db: Session = Depends(get_db)) -> Note:
    return create_note(db, user.id, payload)


@router.get("/{note_id}", response_model=NoteRead)
def get(note_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> Note:
    return owned_note(db, note_id, user.id)


@router.patch("/{note_id}", response_model=NoteRead)
def update(note_id: int, payload: NoteUpdate, user: CurrentUser, db: Session = Depends(get_db)) -> Note:
    return update_note(db, owned_note(db, note_id, user.id), payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(note_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> None:
    note = owned_note(db, note_id, user.id)
    db.delete(note)
    db.commit()
