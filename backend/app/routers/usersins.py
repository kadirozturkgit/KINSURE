"""Authenticated USERSINS CRUD endpoints and username/full-name search."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from ..dependencies import CurrentUser, Database
from ..logging_config import log_operation
from ..schemas import UserCreate, UserRead, UserUpdate
from ..services.usersins import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)

router = APIRouter(prefix="/usersins", tags=["Kullanıcılar"])


@router.get("", response_model=list[UserRead])
def search_users(
    connection: Database,
    _actor: CurrentUser,
    username: str | None = None,
    full_name: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[UserRead]:
    """Search by exact username or partial full name."""
    return list_users(connection, username, full_name, offset, limit)


@router.get("/{username}", response_model=UserRead)
def read_user(username: str, connection: Database, _actor: CurrentUser) -> UserRead:
    """Return one safe user record without its password hash."""
    user = get_user(connection, username)
    if user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def add_user(
    payload: UserCreate,
    connection: Database,
    actor: CurrentUser,
) -> UserRead:
    """Create a user and hash its password before persistence."""
    user = create_user(connection, payload)
    log_operation("oluşturma", "usersins", actor.username)
    return user


@router.put("/{username}", response_model=UserRead)
def edit_user(
    username: str,
    payload: UserUpdate,
    connection: Database,
    actor: CurrentUser,
) -> UserRead:
    """Update a user without changing its username primary key."""
    user = update_user(connection, username, payload)
    log_operation("güncelleme", "usersins", actor.username)
    return user


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(
    username: str,
    connection: Database,
    actor: CurrentUser,
) -> Response:
    """Delete a user by its username primary key."""
    delete_user(connection, username)
    log_operation("silme", "usersins", actor.username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
