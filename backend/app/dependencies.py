"""Shared FastAPI dependencies for Oracle access and authenticated users."""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from .database import Connection, get_connection
from .schemas import UserRead
from .security import decode_access_token
from .services.usersins import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
Database = Annotated[Connection, Depends(get_connection)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    connection: Database,
) -> UserRead:
    """Validate the bearer token and ensure its user still exists and is active."""
    try:
        username = decode_access_token(token).get("sub")
    except JWTError as error:
        raise HTTPException(
            status_code=401,
            detail="Oturum geçersiz veya süresi dolmuş.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    if not isinstance(username, str):
        raise HTTPException(
            status_code=401,
            detail="Oturum geçersiz veya süresi dolmuş.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(connection, username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı bulunamadı veya hesabı etkin değil.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[UserRead, Depends(get_current_user)]
