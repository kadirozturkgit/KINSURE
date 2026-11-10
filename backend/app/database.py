"""Oracle Thin-mode connection pool and safe, parameterized query helpers."""

from collections.abc import Generator, Mapping, Sequence
from typing import Any

import oracledb

from fastapi import HTTPException

from .config import settings

Connection = oracledb.Connection
Pool = oracledb.ConnectionPool

_pool: Pool | None = None


def open_pool() -> None:
    """Open the configured Oracle connection pool without requiring Instant Client."""
    global _pool
    if not settings.database_user or not settings.database_dsn:
        _pool = None
        return
    if settings.database_pool_max < settings.database_pool_min:
        raise ValueError("DATABASE_POOL_MAX DATABASE_POOL_MIN değerinden küçük olamaz.")
    _pool = oracledb.create_pool(
        user=settings.database_user,
        password=settings.database_password.get_secret_value(),
        dsn=settings.database_dsn,
        min=settings.database_pool_min,
        max=settings.database_pool_max,
        increment=settings.database_pool_increment,
    )


def close_pool() -> None:
    """Close the Oracle pool during application shutdown."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def get_connection() -> Generator[Connection, None, None]:
    """Yield one pooled connection and rollback unfinished work on failure."""
    if _pool is None:
        raise HTTPException(
            status_code=503,
            detail="Veritabanı bağlantısı yapılandırılmamış veya kullanılamıyor.",
        )
    connection = _pool.acquire()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    finally:
        _pool.release(connection)


def row_to_dict(cursor: oracledb.Cursor, row: Sequence[Any]) -> dict[str, Any]:
    """Convert an Oracle result row to the API's lowercase field names."""
    return {
        column[0].lower(): value
        for column, value in zip(cursor.description or (), row)
    }


def fetch_one(
    connection: Connection,
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Run a bound SELECT and return at most one mapped row."""
    with connection.cursor() as cursor:
        cursor.execute(statement, parameters or {})
        row = cursor.fetchone()
        return row_to_dict(cursor, row) if row is not None else None


def fetch_all(
    connection: Connection,
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Run a bound SELECT and return mapped rows."""
    with connection.cursor() as cursor:
        cursor.execute(statement, parameters or {})
        return [row_to_dict(cursor, row) for row in cursor.fetchall()]


def execute(
    connection: Connection,
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> None:
    """Run a bound DML statement and commit its transaction."""
    with connection.cursor() as cursor:
        cursor.execute(statement, parameters or {})
    connection.commit()
