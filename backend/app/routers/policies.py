"""Authenticated policy CRUD and policy-search endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from ..dependencies import CurrentUser, Database
from ..logging_config import log_operation
from ..schemas import ApiDate, PolicyCreate, PolicyRead, PolicyUpdate
from ..services.policies import (
    create_policy,
    delete_policy,
    get_policy,
    list_policies,
    update_policy,
)

router = APIRouter(prefix="/policies", tags=["Poliçeler"])


@router.get("", response_model=list[PolicyRead])
def search_policies(
    connection: Database,
    _actor: CurrentUser,
    tckn_vkn: str | None = None,
    product_type: str | None = None,
    start_date: ApiDate | None = None,
    end_date: ApiDate | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[PolicyRead]:
    """Search policies by customer, product, dates, and status."""
    return list_policies(
        connection,
        tckn_vkn,
        product_type,
        start_date,
        end_date,
        status_filter,
        offset,
        limit,
    )


@router.get("/{policy_id}", response_model=PolicyRead)
def read_policy(
    policy_id: int,
    connection: Database,
    _actor: CurrentUser,
) -> PolicyRead:
    """Read one policy by its generated identifier."""
    policy = get_policy(connection, policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    return policy


@router.post("", response_model=PolicyRead, status_code=status.HTTP_201_CREATED)
def add_policy(
    payload: PolicyCreate,
    connection: Database,
    actor: CurrentUser,
) -> PolicyRead:
    """Create a policy and derive its creator from the authenticated session."""
    policy = create_policy(connection, payload, actor.username)
    log_operation("oluşturma", "policies", actor.username)
    return policy


@router.put("/{policy_id}", response_model=PolicyRead)
def edit_policy(
    policy_id: int,
    payload: PolicyUpdate,
    connection: Database,
    actor: CurrentUser,
) -> PolicyRead:
    """Update editable policy fields without changing CREATED_BY."""
    policy = update_policy(connection, policy_id, payload)
    log_operation("güncelleme", "policies", actor.username)
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_policy(
    policy_id: int,
    connection: Database,
    actor: CurrentUser,
) -> Response:
    """Delete one policy by its generated identifier."""
    delete_policy(connection, policy_id)
    log_operation("silme", "policies", actor.username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
