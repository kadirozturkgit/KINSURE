"""Policy CRUD, customer/product validation, and policy-screen search services."""

from datetime import date
from typing import Any

from fastapi import HTTPException

from ..database import Connection, execute, fetch_all, fetch_one
from ..schemas import PolicyCreate, PolicyRead, PolicyUpdate

_COLUMNS = (
    "POLICY_ID, POLICY_NO, TCKN_VKN, PRODUCT_TYPE, START_DATE, END_DATE, "
    "PREMIUM_AMOUNT, STATUS, CREATED_BY, CREATED_AT"
)


def get_policy(connection: Connection, policy_id: int) -> PolicyRead | None:
    """Find one policy by its generated primary key."""
    row = fetch_one(
        connection,
        f"SELECT {_COLUMNS} FROM POLICIES WHERE POLICY_ID = :policy_id",
        {"policy_id": policy_id},
    )
    return PolicyRead.model_validate(row) if row is not None else None


def list_policies(
    connection: Connection,
    tckn_vkn: str | None,
    product_type: str | None,
    start_date: date | None,
    end_date: date | None,
    status: str | None,
    offset: int,
    limit: int,
) -> list[PolicyRead]:
    """Search policies using the exact fields available on the policy search screen."""
    filters: list[str] = []
    parameters: dict[str, Any] = {"offset": offset, "limit": limit}
    for field, value, column in (
        ("tckn_vkn", tckn_vkn, "TCKN_VKN"),
        ("product_type", product_type, "PRODUCT_TYPE"),
        ("start_date", start_date, "START_DATE"),
        ("end_date", end_date, "END_DATE"),
        ("status", status, "STATUS"),
    ):
        if value is not None:
            filters.append(f"{column} = :{field}")
            parameters[field] = value
    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    rows = fetch_all(
        connection,
        f"""
        SELECT {_COLUMNS}
        FROM POLICIES{where_clause}
        ORDER BY POLICY_ID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """,
        parameters,
    )
    return [PolicyRead.model_validate(row) for row in rows]


def create_policy(
    connection: Connection,
    policy: PolicyCreate,
    created_by: str,
) -> PolicyRead:
    """Validate the customer and product type before creating a generated policy."""
    customer = fetch_one(
        connection,
        "SELECT TCKN_VKN FROM CUSTOMERS WHERE TCKN_VKN = :tckn_vkn",
        {"tckn_vkn": policy.tckn_vkn},
    )
    if customer is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    product = fetch_one(
        connection,
        "SELECT PRODUCT_TYPE FROM PRODUCT_TYPES WHERE PRODUCT_TYPE = :product_type",
        {"product_type": policy.product_type},
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Ürün türü bulunamadı.")
    with connection.cursor() as cursor:
        policy_id_variable = cursor.var(int)
        cursor.execute(
            """
            INSERT INTO POLICIES
                (TCKN_VKN, PRODUCT_TYPE, START_DATE, END_DATE, PREMIUM_AMOUNT,
                 STATUS, CREATED_BY)
            VALUES
                (:tckn_vkn, :product_type, :start_date, :end_date, :premium_amount,
                 :status, :created_by)
            RETURNING POLICY_ID INTO :policy_id
            """,
            {
                **policy.model_dump(),
                "start_date": policy.start_date,
                "end_date": policy.end_date,
                "created_by": created_by,
                "policy_id": policy_id_variable,
            },
        )
        policy_id = int(policy_id_variable.getvalue()[0])
    connection.commit()
    created_policy = get_policy(connection, policy_id)
    if created_policy is None:
        raise HTTPException(status_code=500, detail="Poliçe kaydı oluşturulamadı.")
    return created_policy


def update_policy(
    connection: Connection,
    policy_id: int,
    changes: PolicyUpdate,
) -> PolicyRead:
    """Update editable policy fields without changing policy or creator identities."""
    current_policy = get_policy(connection, policy_id)
    if current_policy is None:
        raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    values = changes.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=400,
            detail="Güncellenecek en az bir alan gönderilmelidir.",
        )
    for field in ("start_date", "end_date"):
        if field in values:
            values[field] = getattr(changes, field)
    if "product_type" in values:
        product = fetch_one(
            connection,
            "SELECT PRODUCT_TYPE FROM PRODUCT_TYPES WHERE PRODUCT_TYPE = :product_type",
            {"product_type": values["product_type"]},
        )
        if product is None:
            raise HTTPException(status_code=404, detail="Ürün türü bulunamadı.")
    if "tckn_vkn" in values:
        customer = fetch_one(
            connection,
            "SELECT TCKN_VKN FROM CUSTOMERS WHERE TCKN_VKN = :tckn_vkn",
            {"tckn_vkn": values["tckn_vkn"]},
        )
        if customer is None:
            raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    start_date = values.get("start_date", current_policy.start_date)
    end_date = values.get("end_date", current_policy.end_date)
    if end_date <= start_date:
        raise HTTPException(
            status_code=400,
            detail="Bitiş tarihi başlangıç tarihinden sonra olmalıdır.",
        )
    columns = {
        "tckn_vkn": "TCKN_VKN",
        "product_type": "PRODUCT_TYPE",
        "start_date": "START_DATE",
        "end_date": "END_DATE",
        "premium_amount": "PREMIUM_AMOUNT",
        "status": "STATUS",
    }
    assignments = [f"{columns[field]} = :{field}" for field in values]
    parameters = {**values, "policy_id": policy_id}
    execute(
        connection,
        f"UPDATE POLICIES SET {', '.join(assignments)} WHERE POLICY_ID = :policy_id",
        parameters,
    )
    updated_policy = get_policy(connection, policy_id)
    if updated_policy is None:
        raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    return updated_policy


def delete_policy(connection: Connection, policy_id: int) -> None:
    """Delete one policy by primary key."""
    if get_policy(connection, policy_id) is None:
        raise HTTPException(status_code=404, detail="Poliçe bulunamadı.")
    execute(
        connection,
        "DELETE FROM POLICIES WHERE POLICY_ID = :policy_id",
        {"policy_id": policy_id},
    )
