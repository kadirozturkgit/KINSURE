"""Authenticated customer CRUD and read-only customer lookup endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from ..dependencies import CurrentUser, Database
from ..logging_config import log_operation
from ..schemas import CustomerCreate, CustomerLookup, CustomerRead, CustomerUpdate
from ..services.customers import (
    create_customer,
    delete_customer,
    get_customer,
    get_customer_lookup,
    list_customers,
    update_customer,
)

router = APIRouter(prefix="/customers", tags=["Müşteriler"])


@router.get("", response_model=list[CustomerRead])
def search_customers(
    connection: Database,
    _actor: CurrentUser,
    tckn_vkn: str | None = None,
    name: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[CustomerRead]:
    """Search customers by identity or first/last name."""
    return list_customers(connection, tckn_vkn, name, offset, limit)


@router.get("/lookup/{tckn_vkn}", response_model=CustomerLookup)
def lookup_customer(
    tckn_vkn: str,
    connection: Database,
    _actor: CurrentUser,
) -> CustomerLookup:
    """Return the read-only customer fields required by the policy screen."""
    customer = get_customer_lookup(connection, tckn_vkn)
    if customer is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    return customer


@router.get("/{tckn_vkn}", response_model=CustomerRead)
def read_customer(
    tckn_vkn: str,
    connection: Database,
    _actor: CurrentUser,
) -> CustomerRead:
    """Read one customer record."""
    customer = get_customer(connection, tckn_vkn)
    if customer is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    return customer


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def add_customer(
    payload: CustomerCreate,
    connection: Database,
    actor: CurrentUser,
) -> CustomerRead:
    """Create a customer and set CREATED_BY from the signed-in user."""
    customer = create_customer(connection, payload, actor.username)
    log_operation("oluşturma", "customers", actor.username)
    return customer


@router.put("/{tckn_vkn}", response_model=CustomerRead)
def edit_customer(
    tckn_vkn: str,
    payload: CustomerUpdate,
    connection: Database,
    actor: CurrentUser,
) -> CustomerRead:
    """Update customer details while preserving CREATED_BY."""
    customer = update_customer(connection, tckn_vkn, payload)
    log_operation("güncelleme", "customers", actor.username)
    return customer


@router.delete("/{tckn_vkn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_customer(
    tckn_vkn: str,
    connection: Database,
    actor: CurrentUser,
) -> Response:
    """Delete a customer by TCKN/VKN primary key."""
    delete_customer(connection, tckn_vkn)
    log_operation("silme", "customers", actor.username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
