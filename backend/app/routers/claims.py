"""Authenticated claims CRUD and policy/customer lookup endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from ..dependencies import CurrentUser, Database
from ..logging_config import log_operation
from ..schemas import ClaimCreate, ClaimPolicyContext, ClaimRead, ClaimUpdate
from ..services.claims import (
    create_claim,
    delete_claim,
    get_claim,
    get_claim_policy_context,
    list_claims,
    update_claim,
)

router = APIRouter(prefix="/claims", tags=["Hasarlar"])


@router.get("", response_model=list[ClaimRead])
def search_claims(
    connection: Database,
    _actor: CurrentUser,
    policy_id: int | None = None,
    claim_no: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[ClaimRead]:
    """List claims with optional policy and claim-number filters."""
    return list_claims(connection, policy_id, claim_no, offset, limit)


@router.get("/policy/{policy_id}")
def read_claim_policy(
    policy_id: int,
    connection: Database,
    _actor: CurrentUser,
) -> ClaimPolicyContext:
    """Return policy details and read-only customer fields for the claim screen."""
    context = get_claim_policy_context(connection, policy_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    return ClaimPolicyContext.model_validate(context)


@router.get("/{claim_id}", response_model=ClaimRead)
def read_claim(
    claim_id: int,
    connection: Database,
    _actor: CurrentUser,
) -> ClaimRead:
    """Read one claim by its generated identifier."""
    claim = get_claim(connection, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Hasar kaydı bulunamadı.")
    return claim


@router.post("", response_model=ClaimRead, status_code=status.HTTP_201_CREATED)
def add_claim(
    payload: ClaimCreate,
    connection: Database,
    actor: CurrentUser,
) -> ClaimRead:
    """Create a claim after confirming its policy exists."""
    claim = create_claim(connection, payload, actor.username)
    log_operation("oluşturma", "claims", actor.username)
    return claim


@router.put("/{claim_id}", response_model=ClaimRead)
def edit_claim(
    claim_id: int,
    payload: ClaimUpdate,
    connection: Database,
    actor: CurrentUser,
) -> ClaimRead:
    """Update editable claim fields without changing CREATED_BY."""
    claim = update_claim(connection, claim_id, payload)
    log_operation("güncelleme", "claims", actor.username)
    return claim


@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_claim(
    claim_id: int,
    connection: Database,
    actor: CurrentUser,
) -> Response:
    """Delete a claim by its generated identifier."""
    delete_claim(connection, claim_id)
    log_operation("silme", "claims", actor.username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
