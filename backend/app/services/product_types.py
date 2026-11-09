"""CRUD services for policy product types."""

from typing import Any

from fastapi import HTTPException

from ..database import Connection, execute, fetch_all, fetch_one
from ..schemas import ProductTypeCreate, ProductTypeRead, ProductTypeUpdate

_COLUMNS = "PRODUCT_TYPE, PRODUCT_NAME"


def get_product_type(
    connection: Connection,
    product_type: str,
) -> ProductTypeRead | None:
    """Find one product type by its primary key."""
    row = fetch_one(
        connection,
        f"SELECT {_COLUMNS} FROM PRODUCT_TYPES WHERE PRODUCT_TYPE = :product_type",
        {"product_type": product_type},
    )
    return ProductTypeRead.model_validate(row) if row is not None else None


def list_product_types(
    connection: Connection,
    name: str | None,
    offset: int,
    limit: int,
) -> list[ProductTypeRead]:
    """List product types, optionally filtering by a partial display name."""
    where_clause = (
        " WHERE UPPER(PRODUCT_NAME) LIKE '%' || UPPER(:name) || '%'"
        if name
        else ""
    )
    parameters: dict[str, Any] = {"offset": offset, "limit": limit}
    if name:
        parameters["name"] = name
    rows = fetch_all(
        connection,
        f"""
        SELECT {_COLUMNS}
        FROM PRODUCT_TYPES{where_clause}
        ORDER BY PRODUCT_TYPE
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """,
        parameters,
    )
    return [ProductTypeRead.model_validate(row) for row in rows]


def create_product_type(
    connection: Connection,
    product: ProductTypeCreate,
) -> ProductTypeRead:
    """Insert a product type using bound values."""
    execute(
        connection,
        """
        INSERT INTO PRODUCT_TYPES (PRODUCT_TYPE, PRODUCT_NAME)
        VALUES (:product_type, :product_name)
        """,
        product.model_dump(),
    )
    created_product = get_product_type(connection, product.product_type)
    if created_product is None:
        raise HTTPException(
            status_code=500,
            detail="Ürün türü kaydı oluşturulamadı.",
        )
    return created_product


def update_product_type(
    connection: Connection,
    product_type: str,
    changes: ProductTypeUpdate,
) -> ProductTypeRead:
    """Update the product name while preserving its primary key."""
    if get_product_type(connection, product_type) is None:
        raise HTTPException(status_code=404, detail="Ürün türü bulunamadı.")
    execute(
        connection,
        """
        UPDATE PRODUCT_TYPES
        SET PRODUCT_NAME = :product_name
        WHERE PRODUCT_TYPE = :product_type
        """,
        {"product_name": changes.product_name, "product_type": product_type},
    )
    updated_product = get_product_type(connection, product_type)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Ürün türü bulunamadı.")
    return updated_product


def delete_product_type(connection: Connection, product_type: str) -> None:
    """Delete one product type by primary key."""
    if get_product_type(connection, product_type) is None:
        raise HTTPException(status_code=404, detail="Ürün türü bulunamadı.")
    execute(
        connection,
        "DELETE FROM PRODUCT_TYPES WHERE PRODUCT_TYPE = :product_type",
        {"product_type": product_type},
    )
