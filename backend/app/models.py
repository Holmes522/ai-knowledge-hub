from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class NoteStatus(str, Enum):
    UNLEARNED = "unlearned"
    LEARNING = "learning"
    COMPLETED = "completed"
    REVIEWING = "reviewing"


class TagType(str, Enum):
    FORMAT = "format"
    CATEGORY = "category"
    CUSTOM = "custom"


note_tags = Table(
    "note_tag",
    Base.metadata,
    Column("note_id", ForeignKey("note.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.USER)
    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    notes: Mapped[list["Note"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(500), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[NoteStatus] = mapped_column(SqlEnum(NoteStatus), default=NoteStatus.UNLEARNED)
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    owner: Mapped[User] = relationship(back_populates="notes")
    tags: Mapped[list["Tag"]] = relationship(secondary=note_tags, back_populates="notes")
    files: Mapped[list["NoteFile"]] = relationship(back_populates="note", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = (UniqueConstraint("name", "type", name="uq_tag_name_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    type: Mapped[TagType] = mapped_column(SqlEnum(TagType), default=TagType.CUSTOM)
    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    notes: Mapped[list[Note]] = relationship(secondary=note_tags, back_populates="tags")


class NoteFile(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("note.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(100))
    file_url: Mapped[str] = mapped_column(String(500), unique=True)
    file_size: Mapped[int] = mapped_column(Integer)
    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    note: Mapped[Note] = relationship(back_populates="files")
