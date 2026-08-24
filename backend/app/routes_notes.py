from fastapi import APIRouter, Depends, File as UploadFileParam, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .dependencies import CurrentUser
from .models import Note, NoteFile
from .schemas import FileRead, NoteCreate, NoteList, NoteRead, NoteUpdate
from .services import create_note, search_notes, update_note
from .storage import remove_upload, save_upload

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


@router.get("/{note_id}/files", response_model=list[FileRead])
def list_files(note_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> list[NoteFile]:
    owned_note(db, note_id, user.id)
    return list(db.scalars(select(NoteFile).where(NoteFile.note_id == note_id).order_by(NoteFile.created_time.desc())))


@router.post("/{note_id}/files", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    note_id: int,
    user: CurrentUser,
    db: Session = Depends(get_db),
    file: UploadFile = UploadFileParam(...),
) -> NoteFile:
    owned_note(db, note_id, user.id)
    relative_path, content_type, file_size = await save_upload(file, note_id)
    stored = NoteFile(
        note_id=note_id,
        filename=file.filename or "attachment",
        file_type=content_type,
        file_url=f"/uploads/{relative_path}",
        file_size=file_size,
    )
    db.add(stored)
    db.commit()
    db.refresh(stored)
    return stored


@router.delete("/{note_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(note_id: int, file_id: int, user: CurrentUser, db: Session = Depends(get_db)) -> None:
    owned_note(db, note_id, user.id)
    stored = db.scalar(select(NoteFile).where(NoteFile.id == file_id, NoteFile.note_id == note_id))
    if not stored:
        raise HTTPException(status_code=404, detail="File not found")
    relative_path = stored.file_url.removeprefix("/uploads/")
    db.delete(stored)
    db.commit()
    remove_upload(relative_path)
