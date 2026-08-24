from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import get_db
from .dependencies import AdminUser
from .models import Comment, CommentStatus, Note, User
from .schemas import AdminStats, CommentModerate, CommentRead

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/comments", response_model=list[CommentRead])
def list_comments(_: AdminUser, db: Session = Depends(get_db)) -> list[Comment]:
    return list(db.scalars(select(Comment).order_by(Comment.created_time.desc())))


@router.patch("/comments/{comment_id}", response_model=CommentRead)
def moderate_comment(comment_id: int, payload: CommentModerate, _: AdminUser, db: Session = Depends(get_db)) -> Comment:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.status = CommentStatus(payload.status)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/stats", response_model=AdminStats)
def stats(_: AdminUser, db: Session = Depends(get_db)) -> AdminStats:
    return AdminStats(
        notes=db.scalar(select(func.count(Note.id))) or 0,
        users=db.scalar(select(func.count(User.id))) or 0,
        comments=db.scalar(select(func.count(Comment.id))) or 0,
        views=db.scalar(select(func.coalesce(func.sum(Note.views), 0))) or 0,
    )
