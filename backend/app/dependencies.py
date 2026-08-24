from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .db import get_db
from .models import User, UserRole
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]
) -> User:
    subject = decode_access_token(token)
    user = db.get(User, int(subject)) if subject and subject.isdigit() else None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_admin_user(user: CurrentUser) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user


AdminUser = Annotated[User, Depends(get_admin_user)]
