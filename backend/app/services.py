from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .models import Note, NoteStatus, Tag, TagType
from .schemas import NoteCreate, NoteUpdate


def normalized_tag_name(name: str) -> str:
    return " ".join(name.strip().split())


def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    for raw_name in names:
        name = normalized_tag_name(raw_name)
        if not name:
            continue
        tag = db.scalar(select(Tag).where(Tag.name == name, Tag.type == TagType.CUSTOM))
        if tag is None:
            tag = Tag(name=name, type=TagType.CUSTOM)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def create_note(db: Session, user_id: int, payload: NoteCreate) -> Note:
    note = Note(
        user_id=user_id,
        title=payload.title.strip(),
        summary=payload.summary.strip(),
        content=payload.content,
        tags=get_or_create_tags(db, payload.tags),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(db: Session, note: Note, payload: NoteUpdate) -> Note:
    values = payload.model_dump(exclude_unset=True)
    tag_names = values.pop("tags", None)
    for key, value in values.items():
        setattr(note, key, value.strip() if isinstance(value, str) and key in {"title", "summary"} else value)
    if tag_names is not None:
        note.tags = get_or_create_tags(db, tag_names)
    db.commit()
    db.refresh(note)
    return note


def search_notes(db: Session, user_id: int, query: str | None) -> tuple[list[Note], int]:
    statement = select(Note).where(Note.user_id == user_id)
    if query and query.strip():
        term = f"%{query.strip()}%"
        statement = statement.where(
            or_(Note.title.ilike(term), Note.summary.ilike(term), Note.content.ilike(term), Note.tags.any(Tag.name.ilike(term)))
        )
    statement = statement.order_by(Note.updated_time.desc(), Note.id.desc())
    items = list(db.scalars(statement).unique())
    return items, len(items)
