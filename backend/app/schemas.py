from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    avatar: str | None
    role: str
    created_time: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=500)
    content: str = ""
    tags: list[str] = Field(default_factory=list, max_length=20)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str | None = None
    status: Literal["unlearned", "learning", "completed", "reviewing"] | None = None
    tags: list[str] | None = Field(default=None, max_length=20)
    is_public: bool | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str
    content: str
    status: str
    views: int
    is_public: bool
    created_time: datetime
    updated_time: datetime
    tags: list[TagRead]


class NoteList(BaseModel):
    items: list[NoteRead]
    total: int


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    note_id: int
    filename: str
    file_type: str
    file_url: str
    file_size: int
    created_time: datetime


class PublicCommentCreate(BaseModel):
    nickname: str = Field(min_length=1, max_length=80)
    email: EmailStr
    content: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    note_id: int
    user_id: int | None
    nickname: str
    email: EmailStr
    content: str
    status: str
    created_time: datetime


class CommentModerate(BaseModel):
    status: Literal["approved", "rejected"]


class AdminStats(BaseModel):
    notes: int
    users: int
    comments: int
    views: int


class IndexResult(BaseModel):
    note_id: int
    chunks: int


class AIQuestion(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


class AISource(BaseModel):
    note_id: int
    title: str
    excerpt: str
    score: float


class AIAnswer(BaseModel):
    answer: str
    sources: list[AISource]
