"""FastAPI application, lifecycle hooks, Turkish exception responses, and routes."""

from contextlib import asynccontextmanager
import logging
from collections.abc import AsyncIterator
import os

import oracledb
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .database import close_pool, open_pool
from .logging_config import configure_logging
from .routers import auth, claims, customers, policies, product_types, usersins

error_logger = logging.getLogger("kinsure.errors")


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Configure logs and the Oracle pool for the application lifetime."""
    configure_logging()
    if (
        "jwt_secret_key" not in settings.model_fields_set
        and not os.getenv("JWT_SECRET_KEY")
    ):
        error_logger.warning(
            "JWT_SECRET_KEY yapılandırılmadı; süreç için geçici anahtar kullanılacak."
        )
    if (
        not settings.database_user
        or not settings.database_dsn
        or not settings.database_password.get_secret_value()
    ):
        error_logger.error(
            "Oracle bağlantı ayarları eksik; veritabanı uç noktaları kullanılamaz."
        )
    else:
        open_pool()
    try:
        yield
    finally:
        close_pool()


app = FastAPI(
    title="KINSURE API",
    description="KINSURE sigortacılık yönetim sistemi backend servisi.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
for router in (
    usersins.router,
    customers.router,
    product_types.router,
    policies.router,
    claims.router,
):
    app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["Sağlık"])
def health_check() -> dict[str, str]:
    """Expose a lightweight process health endpoint."""
    return {"durum": "çalışıyor"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Return Turkish validation messages without leaking framework wording."""
    field_errors = [
        {
            "alan": ".".join(str(part) for part in item["loc"][1:]),
            "mesaj": "Alan değeri geçersiz.",
        }
        for item in error.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Gönderilen bilgiler doğrulanamadı.",
            "errors": field_errors,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request,
    error: StarletteHTTPException,
) -> JSONResponse:
    """Translate framework-generated HTTP messages while preserving API errors."""
    default_messages = {
        401: "Kimlik doğrulaması gereklidir.",
        403: "Bu işlem için yetkiniz yok.",
        404: "İstenen kaynak bulunamadı.",
        405: "Bu HTTP yöntemi bu uç noktada desteklenmiyor.",
    }
    detail = error.detail
    if not isinstance(detail, str) or detail in {
        "Not Found",
        "Method Not Allowed",
        "Not authenticated",
    }:
        detail = default_messages.get(error.status_code, "İstek tamamlanamadı.")
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": detail},
        headers=error.headers,
    )


@app.exception_handler(oracledb.Error)
async def oracle_exception_handler(
    _request: Request,
    error: oracledb.Error,
) -> JSONResponse:
    """Map common Oracle constraint errors to Turkish client-safe messages."""
    error_logger.exception("Oracle veritabanı işlemi başarısız oldu.")
    oracle_error = error.args[0] if error.args else None
    code = getattr(oracle_error, "code", None)
    if code == 1:
        return JSONResponse(
            status_code=409,
            content={"detail": "Bu kayıt zaten mevcut."},
        )
    if code in {1400, 2290, 2291, 2292}:
        return JSONResponse(
            status_code=400,
            content={"detail": "İşlem, ilişkili kayıt veya alan kurallarına aykırı."},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Veritabanı işlemi tamamlanamadı."},
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    _request: Request,
    error: Exception,
) -> JSONResponse:
    """Log unexpected failures and return a consistent Turkish error response."""
    error_logger.exception("Beklenmeyen API hatası oluştu.")
    return JSONResponse(
        status_code=500,
        content={"detail": "Beklenmeyen bir sunucu hatası oluştu."},
    )
