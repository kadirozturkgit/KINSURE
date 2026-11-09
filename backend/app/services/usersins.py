"""USERSINS CRUD and account lookup services with one-way password hashing."""

from typing import Any

from fastapi import HTTPException

from ..database import Connection, execute, fetch_all, fetch_one
from ..schemas import UserCreate, UserRead, UserRegistration, UserUpdate
from ..security import hash_password

_PUBLIC_COLUMNS = (
    "USERNAME, FULL_NAME, EMAIL, ROLE, IS_ACTIVE, CREATED_AT, UPDATED_AT"
)


def get_user(connection: Connection, username: str) -> UserRead | None:
    """Find a user by its primary key without returning PASSWORD_HASH."""
    row = fetch_one(
        connection,
        f"SELECT {_PUBLIC_COLUMNS} FROM USERSINS WHERE USERNAME = :username",
        {"username": username},
    )
    return UserRead.model_validate(row) if row is not None else None


def get_user_hash(connection: Connection, username: str) -> str | None:
    """Read the stored hash for authentication without exposing it through the API."""
    row = fetch_one(
        connection,
        "SELECT PASSWORD_HASH FROM USERSINS WHERE USERNAME = :username",
        {"username": username},
    )
    return str(row["password_hash"]) if row is not None else None


def list_users(
    connection: Connection,
    username: str | None,
    full_name: str | None,
    offset: int,
    limit: int,
) -> list[UserRead]:
    """Search users by username or full name and return a bounded result page."""
    filters: list[str] = []
    parameters: dict[str, Any] = {"offset": offset, "limit": limit}
    if username and full_name:
        filters.append(
            "(USERNAME = :username OR UPPER(FULL_NAME) LIKE "
            "'%' || UPPER(:full_name) || '%')"
        )
        parameters.update({"username": username, "full_name": full_name})
    elif username:
        filters.append("USERNAME = :username")
        parameters["username"] = username
    elif full_name:
        filters.append("UPPER(FULL_NAME) LIKE '%' || UPPER(:full_name) || '%'")
        parameters["full_name"] = full_name
    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    rows = fetch_all(
        connection,
        f"""
        SELECT {_PUBLIC_COLUMNS}
        FROM USERSINS{where_clause}
        ORDER BY USERNAME
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """,
        parameters,
    )
    return [UserRead.model_validate(row) for row in rows]


def create_user(
    connection: Connection,
    user: UserCreate | UserRegistration,
    *,
    role: str | None = None,
) -> UserRead:
    """Create a user after hashing the supplied password."""
    assigned_role = role or (user.role if isinstance(user, UserCreate) else "USER")
    is_active = user.is_active if isinstance(user, UserCreate) else True
    execute(
        connection,
        """
        INSERT INTO USERSINS
            (USERNAME, PASSWORD_HASH, FULL_NAME, EMAIL, ROLE, IS_ACTIVE)
        VALUES
            (:username, :password_hash, :full_name, :email, :role, :is_active)
        """,
        {
            "username": user.username,
            "password_hash": hash_password(user.password),
            "full_name": user.full_name,
            "email": str(user.email),
            "role": assigned_role,
            "is_active": 1 if is_active else 0,
        },
    )
    created_user = get_user(connection, user.username)
    if created_user is None:
        raise HTTPException(status_code=500, detail="Kullanıcı kaydı oluşturulamadı.")
    return created_user


def update_user(
    connection: Connection,
    username: str,
    changes: UserUpdate,
) -> UserRead:
    """Update supplied user fields while hashing any replacement password."""
    current_user = get_user(connection, username)
    if current_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    values = changes.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=400,
            detail="Güncellenecek en az bir alan gönderilmelidir.",
        )
    assignments: list[str] = []
    parameters: dict[str, Any] = {"username": username}
    for field, value in values.items():
        column = {
            "password": "PASSWORD_HASH",
            "full_name": "FULL_NAME",
            "email": "EMAIL",
            "role": "ROLE",
            "is_active": "IS_ACTIVE",
        }[field]
        if field == "password":
            value = hash_password(value)
        elif field == "email":
            value = str(value)
        elif field == "is_active":
            value = 1 if value else 0
        assignments.append(f"{column} = :{field}")
        parameters[field] = value
    assignments.append("UPDATED_AT = CURRENT_TIMESTAMP")
    execute(
        connection,
        f"UPDATE USERSINS SET {', '.join(assignments)} WHERE USERNAME = :username",
        parameters,
    )
    updated_user = get_user(connection, username)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return updated_user


def delete_user(connection: Connection, username: str) -> None:
    """Delete one user by primary key."""
    if get_user(connection, username) is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    execute(
        connection,
        "DELETE FROM USERSINS WHERE USERNAME = :username",
        {"username": username},
    )
