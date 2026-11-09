"""Authenticated product type CRUD endpoints for the policy product selector."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from ..dependencies import CurrentUser, Database
from ..logging_config import log_operation
from ..schemas import ProductTypeCreate, ProductTypeRead, ProductTypeUpdate
from ..services.product_types import (
    create_product_type,
    delete_product_type,
    get_product_type,
    list_product_types,
    update_product_type,
)

router = APIRouter(prefix="/product-types", tags=["Ürün türleri"])


@router.get("", response_model=list[ProductTypeRead])
def search_product_types(
    connection: Database,
    _actor: CurrentUser,
    name: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[ProductTypeRead]:
    """List product types for CRUD and policy selection."""
    return list_product_types(connection, name, offset, limit)


@router.get("/{product_type}", response_model=ProductTypeRead)
def read_product_type(
    product_type: str,
    connection: Database,
    _actor: CurrentUser,
) -> ProductTypeRead:
    """Read one product type by its primary key."""
    product = get_product_type(connection, product_type)
    if product is None:
        raise HTTPException(status_code=404, detail="Ürün türü bulunamadı.")
    return product


@router.post("", response_model=ProductTypeRead, status_code=status.HTTP_201_CREATED)
def add_product_type(
    payload: ProductTypeCreate,
    connection: Database,
    actor: CurrentUser,
) -> ProductTypeRead:
    """Create a product type."""
    product = create_product_type(connection, payload)
    log_operation("oluşturma", "product_types", actor.username)
    return product


@router.put("/{product_type}", response_model=ProductTypeRead)
def edit_product_type(
    product_type: str,
    payload: ProductTypeUpdate,
    connection: Database,
    actor: CurrentUser,
) -> ProductTypeRead:
    """Update a product type's display name."""
    product = update_product_type(connection, product_type, payload)
    log_operation("güncelleme", "product_types", actor.username)
    return product


@router.delete("/{product_type}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product_type(
    product_type: str,
    connection: Database,
    actor: CurrentUser,
) -> Response:
    """Delete one product type."""
    delete_product_type(connection, product_type)
    log_operation("silme", "product_types", actor.username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
