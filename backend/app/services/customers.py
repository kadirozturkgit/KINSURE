"""Customer CRUD, search, and read-only policy/claim screen lookup services."""

from typing import Any

from fastapi import HTTPException

from ..database import Connection, execute, fetch_all, fetch_one
from ..schemas import CustomerCreate, CustomerLookup, CustomerRead, CustomerUpdate

_COLUMNS = (
    "TCKN_VKN, FIRST_NAME, LAST_NAME, EMAIL, PHONE, BIRTH_DATE, "
    "GENDER, ADDRESS, CREATED_BY, CREATED_AT"
)
_LOOKUP_COLUMNS = "TCKN_VKN, FIRST_NAME, LAST_NAME, EMAIL, BIRTH_DATE"


def get_customer(connection: Connection, tckn_vkn: str) -> CustomerRead | None:
    """Find one customer by the TCKN/VKN primary key."""
    row = fetch_one(
        connection,
        f"SELECT {_COLUMNS} FROM CUSTOMERS WHERE TCKN_VKN = :tckn_vkn",
        {"tckn_vkn": tckn_vkn},
    )
    return CustomerRead.model_validate(row) if row is not None else None


def get_customer_lookup(
    connection: Connection,
    tckn_vkn: str,
) -> CustomerLookup | None:
    """Return only the customer fields displayed on policy and claim screens."""
    row = fetch_one(
        connection,
        f"SELECT {_LOOKUP_COLUMNS} FROM CUSTOMERS WHERE TCKN_VKN = :tckn_vkn",
        {"tckn_vkn": tckn_vkn},
    )
    return CustomerLookup.model_validate(row) if row is not None else None


def list_customers(
    connection: Connection,
    tckn_vkn: str | None,
    name: str | None,
    offset: int,
    limit: int,
) -> list[CustomerRead]:
    """Search customers by identity or name with a bounded page size."""
    filters: list[str] = []
    parameters: dict[str, Any] = {"offset": offset, "limit": limit}
    if tckn_vkn:
        filters.append("TCKN_VKN = :tckn_vkn")
        parameters["tckn_vkn"] = tckn_vkn
    if name:
        filters.append(
            "(UPPER(FIRST_NAME) LIKE '%' || UPPER(:name) || '%' "
            "OR UPPER(LAST_NAME) LIKE '%' || UPPER(:name) || '%')"
        )
        parameters["name"] = name
    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    rows = fetch_all(
        connection,
        f"""
        SELECT {_COLUMNS}
        FROM CUSTOMERS{where_clause}
        ORDER BY TCKN_VKN
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """,
        parameters,
    )
    return [CustomerRead.model_validate(row) for row in rows]


def create_customer(
    connection: Connection,
    customer: CustomerCreate,
    created_by: str,
) -> CustomerRead:
    """Insert a customer and derive the audit user from the authenticated session."""
    execute(
        connection,
        """
        INSERT INTO CUSTOMERS
            (TCKN_VKN, FIRST_NAME, LAST_NAME, EMAIL, PHONE, BIRTH_DATE,
             GENDER, ADDRESS, CREATED_BY)
        VALUES
            (:tckn_vkn, :first_name, :last_name, :email, :phone, :birth_date,
             :gender, :address, :created_by)
        """,
        {
            **customer.model_dump(),
            "birth_date": customer.birth_date,
            "email": str(customer.email) if customer.email is not None else None,
            "created_by": created_by,
        },
    )
    created_customer = get_customer(connection, customer.tckn_vkn)
    if created_customer is None:
        raise HTTPException(status_code=500, detail="Müşteri kaydı oluşturulamadı.")
    return created_customer


def update_customer(
    connection: Connection,
    tckn_vkn: str,
    changes: CustomerUpdate,
) -> CustomerRead:
    """Update editable customer fields without changing identity or audit values."""
    if get_customer(connection, tckn_vkn) is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    values = changes.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=400,
            detail="Güncellenecek en az bir alan gönderilmelidir.",
        )
    if "birth_date" in values:
        values["birth_date"] = changes.birth_date
    columns = {
        "first_name": "FIRST_NAME",
        "last_name": "LAST_NAME",
        "email": "EMAIL",
        "phone": "PHONE",
        "birth_date": "BIRTH_DATE",
        "gender": "GENDER",
        "address": "ADDRESS",
    }
    assignments: list[str] = []
    parameters: dict[str, Any] = {"tckn_vkn": tckn_vkn}
    for field, value in values.items():
        assignments.append(f"{columns[field]} = :{field}")
        parameters[field] = str(value) if field == "email" and value else value
    execute(
        connection,
        f"UPDATE CUSTOMERS SET {', '.join(assignments)} WHERE TCKN_VKN = :tckn_vkn",
        parameters,
    )
    updated_customer = get_customer(connection, tckn_vkn)
    if updated_customer is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    return updated_customer


def delete_customer(connection: Connection, tckn_vkn: str) -> None:
    """Delete one customer by primary key."""
    if get_customer(connection, tckn_vkn) is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı.")
    execute(
        connection,
        "DELETE FROM CUSTOMERS WHERE TCKN_VKN = :tckn_vkn",
        {"tckn_vkn": tckn_vkn},
    )
