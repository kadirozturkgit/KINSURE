"""Public registration and password-based login endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..dependencies import Database
from ..logging_config import log_operation
from ..schemas import TokenResponse, UserRead, UserRegistration
from ..security import create_access_token, verify_password
from ..services.usersins import create_user, get_user, get_user_hash

router = APIRouter(prefix="/auth", tags=["Kimlik doğrulama"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegistration, connection: Database) -> UserRead:
    """Register a new account with a server-assigned standard USER role."""
    user = create_user(connection, payload, role="USER")
    log_operation("kayıt", "usersins", user.username)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    connection: Database,
) -> TokenResponse:
    """Authenticate username/password credentials and issue a signed bearer token."""
    user = get_user(connection, form.username)
    password_hash = get_user_hash(connection, form.username)
    if (
        user is None
        or password_hash is None
        or not user.is_active
        or not verify_password(form.password, password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı adı veya şifre hatalı.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    log_operation("giriş", "auth", user.username)
    return TokenResponse(access_token=create_access_token(user.username))
