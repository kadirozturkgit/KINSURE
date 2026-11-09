"""Claims CRUD, policy validation, and read-only policy/customer lookup services."""

from typing import Any

from fastapi import HTTPException

from ..database import Connection, execute, fetch_all, fetch_one
from ..schemas import ClaimCreate, ClaimRead, ClaimUpdate

_COLUMNS = (
    "CLAIM_ID, CLAIM_NO, POLICY_ID, INCIDENT_DATE, CLAIM_DATE, CLAIM_AMOUNT, "
    "PAID_AMOUNT, STATUS, DESCRIPTION, CREATED_BY, CREATED_AT"
)


def get_claim(connection: Connection, claim_id: int) -> ClaimRead | None:
    """Find one claim by its generated primary key."""
    row = fetch_one(
        connection,
        f"SELECT {_COLUMNS} FROM CLAIMS WHERE CLAIM_ID = :claim_id",
        {"claim_id": claim_id},
    )
    return ClaimRead.model_validate(row) if row is not None else None


def list_claims(
    connection: Connection,
    policy_id: int | None,
    claim_no: str | None,
    offset: int,
    limit: int,
) -> list[ClaimRead]:
    """List claims with optional filters and a bounded page size."""
    filters: list[str] = []
    parameters: dict[str, Any] = {"offset": offset, "limit": limit}
    if policy_id is not None:
        filters.append("POLICY_ID = :policy_id")
        parameters["policy_id"] = policy_id
    if claim_no:
        filters.append("CLAIM_NO = :claim_no")
        parameters["claim_no"] = claim_no
    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    rows = fetch_all(
        connection,
        f"""
        SELECT {_COLUMNS}
        FROM CLAIMS{where_clause}
        ORDER BY CLAIM_ID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """,
        parameters,
    )
    return [ClaimRead.model_validate(row) for row in rows]


def get_claim_policy_context(
    connection: Connection,
    policy_id: int,
) -> dict[str, Any] | None:
    """Return policy details and the limited customer fields for the claim screen."""
    return fetch_one(
        connection,
        """
        SELECT P.POLICY_ID, P.POLICY_NO, P.TCKN_VKN, P.PRODUCT_TYPE,
               P.START_DATE, P.END_DATE, P.PREMIUM_AMOUNT, P.STATUS,
               C.FIRST_NAME, C.LAST_NAME, C.EMAIL, C.BIRTH_DATE
        FROM POLICIES P
        JOIN CUSTOMERS C ON C.TCKN_VKN = P.TCKN_VKN
        WHERE P.POLICY_ID = :policy_id
        """,
        {"policy_id": policy_id},
    )


def create_claim(
    connection: Connection,
    claim: ClaimCreate,
    created_by: str,
) -> ClaimRead:
    """Validate the referenced policy and create a database-numbered claim."""
    policy = fetch_one(
        connection,
        "SELECT POLICY_ID FROM POLICIES WHERE POLICY_ID = :policy_id",
        {"policy_id": claim.policy_id},
    )
    if policy is None:
        raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    with connection.cursor() as cursor:
        claim_id_variable = cursor.var(int)
        cursor.execute(
            """
            INSERT INTO CLAIMS
                (POLICY_ID, INCIDENT_DATE, CLAIM_DATE, CLAIM_AMOUNT, PAID_AMOUNT,
                 STATUS, DESCRIPTION, CREATED_BY)
            VALUES
                (:policy_id, :incident_date, :claim_date, :claim_amount, :paid_amount,
                 :status, :description, :created_by)
            RETURNING CLAIM_ID INTO :claim_id
            """,
            {
                **claim.model_dump(),
                "created_by": created_by,
                "claim_id": claim_id_variable,
            },
        )
        claim_id = int(claim_id_variable.getvalue())
    connection.commit()
    created_claim = get_claim(connection, claim_id)
    if created_claim is None:
        raise HTTPException(status_code=500, detail="Hasar kaydı oluşturulamadı.")
    return created_claim


def update_claim(
    connection: Connection,
    claim_id: int,
    changes: ClaimUpdate,
) -> ClaimRead:
    """Update editable claim fields while keeping generated and audit values intact."""
    if get_claim(connection, claim_id) is None:
        raise HTTPException(status_code=404, detail="Hasar kaydı bulunamadı.")
    values = changes.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=400,
            detail="Güncellenecek en az bir alan gönderilmelidir.",
        )
    columns = {
        "policy_id": "POLICY_ID",
        "incident_date": "INCIDENT_DATE",
        "claim_date": "CLAIM_DATE",
        "claim_amount": "CLAIM_AMOUNT",
        "paid_amount": "PAID_AMOUNT",
        "status": "STATUS",
        "description": "DESCRIPTION",
    }
    assignments = [f"{columns[field]} = :{field}" for field in values]
    if "policy_id" in values:
        policy = fetch_one(
            connection,
            "SELECT POLICY_ID FROM POLICIES WHERE POLICY_ID = :policy_id",
            {"policy_id": values["policy_id"]},
        )
        if policy is None:
            raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    execute(
        connection,
        f"UPDATE CLAIMS SET {', '.join(assignments)} WHERE CLAIM_ID = :claim_id",
        {**values, "claim_id": claim_id},
    )
    updated_claim = get_claim(connection, claim_id)
    if updated_claim is None:
        raise HTTPException(status_code=404, detail="Hasar kaydı bulunamadı.")
    return updated_claim


def delete_claim(connection: Connection, claim_id: int) -> None:
    """Delete one claim by primary key."""
    if get_claim(connection, claim_id) is None:
        raise HTTPException(status_code=404, detail="Hasar kaydı bulunamadı.")
    execute(
        connection,
        "DELETE FROM CLAIMS WHERE CLAIM_ID = :claim_id",
        {"claim_id": claim_id},
    )
