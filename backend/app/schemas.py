"""Pydantic request and response models with Turkish date and money formatting."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    model_validator,
    PlainSerializer,
)


def parse_api_date(value: Any) -> Any:
    """Accept API dates as DD/MM/YYYY or ISO dates and normalize Oracle values."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue
    return value


def parse_api_datetime(value: Any) -> Any:
    """Normalize Oracle timestamps and accept Turkish or ISO date-time strings."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        for date_format in (
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ):
            try:
                return datetime.strptime(value, date_format)
            except ValueError:
                continue
    return value


def require_eleven_digits(value: str) -> str:
    """Require the TCKN/VKN value to match the documented 11-digit schema."""
    if len(value) != 11 or not value.isascii() or not value.isdigit():
        raise ValueError("TCKN/VKN 11 rakamdan oluşmalıdır.")
    return value


def require_valid_gender(value: str | None) -> str | None:
    """Restrict gender to the values presented by the customer screen."""
    if value is not None and value not in {"E", "K", "X"}:
        raise ValueError("Cinsiyet E, K veya X olmalıdır.")
    return value


def format_api_date(value: date) -> str:
    """Serialize dates in the DD/MM/YYYY format used by KINSURE screens."""
    return value.strftime("%d/%m/%Y")


def format_api_datetime(value: datetime) -> str:
    """Serialize timestamps with a Turkish date and an explicit time component."""
    return value.strftime("%d/%m/%Y %H:%M:%S")


def format_money(value: Decimal) -> str:
    """Serialize financial amounts with exactly two decimal places."""
    return f"{value:.2f}"


ApiDate = Annotated[
    date,
    BeforeValidator(parse_api_date),
    PlainSerializer(format_api_date, return_type=str),
]
ApiDateTime = Annotated[
    datetime,
    BeforeValidator(parse_api_datetime),
    PlainSerializer(format_api_datetime, return_type=str),
]
Money = Annotated[
    Decimal,
    PlainSerializer(format_money, return_type=str),
]
TcknVkn = Annotated[str, AfterValidator(require_eleven_digits)]


class UserRegistration(BaseModel):
    """Public sign-up payload; the server assigns the non-privileged USER role."""

    username: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=100)


class UserCreate(UserRegistration):
    """Authenticated CRUD payload matching the USERSINS required fields."""

    role: str = Field(min_length=1, max_length=20)
    is_active: bool = True


class UserUpdate(BaseModel):
    """Optional fields accepted when updating a USERSINS record."""

    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, min_length=1, max_length=20)
    is_active: bool | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "UserUpdate":
        """Prevent explicit nulls from violating mandatory database columns."""
        for field in ("password", "full_name", "email", "role", "is_active"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} alanı boş bırakılamaz.")
        return self


class UserRead(BaseModel):
    """Safe USERSINS representation that never exposes PASSWORD_HASH."""

    username: str
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: ApiDateTime | None = None
    updated_at: ApiDateTime | None = None


class CustomerCreate(BaseModel):
    """New customer data; CREATED_BY and CREATED_AT are assigned by the server."""

    tckn_vkn: TcknVkn
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    birth_date: ApiDate | None = None
    gender: Annotated[str | None, AfterValidator(require_valid_gender)] = None
    address: str | None = Field(default=None, max_length=500)


class CustomerUpdate(BaseModel):
    """Editable customer fields; identity and creation audit values are immutable."""

    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    birth_date: ApiDate | None = None
    gender: Annotated[str | None, AfterValidator(require_valid_gender)] = None
    address: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "CustomerUpdate":
        """Prevent explicit nulls from violating mandatory customer columns."""
        for field in ("first_name", "last_name", "phone"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} alanı boş bırakılamaz.")
        return self


class CustomerRead(BaseModel):
    """Full customer representation returned by customer CRUD endpoints."""

    tckn_vkn: str
    first_name: str
    last_name: str
    email: EmailStr | None
    phone: str
    birth_date: ApiDate | None
    gender: str | None
    address: str | None
    created_by: str
    created_at: ApiDateTime | None


class CustomerLookup(BaseModel):
    """Read-only customer fields needed by policy and claim screens."""

    tckn_vkn: str
    first_name: str
    last_name: str
    email: EmailStr | None
    birth_date: ApiDate | None


class ProductTypeCreate(BaseModel):
    """New product type values matching the PRODUCT_TYPES table."""

    product_type: str = Field(min_length=1, max_length=5)
    product_name: str = Field(min_length=1, max_length=50)


class ProductTypeUpdate(BaseModel):
    """Editable product name; product type key remains immutable."""

    product_name: str = Field(min_length=1, max_length=50)


class ProductTypeRead(BaseModel):
    """Product type representation used by the CRUD and policy selector APIs."""

    product_type: str
    product_name: str


class PolicyCreate(BaseModel):
    """New policy data; keys, policy number, and creator are assigned server-side."""

    tckn_vkn: TcknVkn
    product_type: str = Field(min_length=1, max_length=5)
    start_date: ApiDate
    end_date: ApiDate
    premium_amount: Decimal = Field(ge=Decimal("0"), max_digits=15, decimal_places=2)
    status: str = Field(default="ACTIVE", min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_policy_dates(self) -> "PolicyCreate":
        """Ensure policy coverage ends after it begins."""
        if self.end_date <= self.start_date:
            raise ValueError("Bitiş tarihi başlangıç tarihinden sonra olmalıdır.")
        return self


class PolicyUpdate(BaseModel):
    """Editable policy fields; policy ID, number, and audit values are immutable."""

    tckn_vkn: TcknVkn | None = None
    product_type: str | None = Field(default=None, min_length=1, max_length=5)
    start_date: ApiDate | None = None
    end_date: ApiDate | None = None
    premium_amount: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
    )
    status: str | None = Field(default=None, min_length=1, max_length=20)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "PolicyUpdate":
        """Prevent nulls from bypassing the policy's required database columns."""
        for field in (
            "tckn_vkn",
            "product_type",
            "start_date",
            "end_date",
            "premium_amount",
            "status",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} alanı boş bırakılamaz.")
        return self


class PolicyRead(BaseModel):
    """Policy fields required by the policy and claim screens."""

    policy_id: int
    policy_no: str | None
    tckn_vkn: str
    product_type: str
    start_date: ApiDate
    end_date: ApiDate
    premium_amount: Money
    status: str | None
    created_by: str
    created_at: ApiDateTime | None


class ClaimCreate(BaseModel):
    """New claim data; claim ID, number, and creator are server-side values."""

    policy_id: int = Field(gt=0)
    incident_date: ApiDate
    claim_date: ApiDate
    claim_amount: Decimal = Field(ge=Decimal("0"), max_digits=15, decimal_places=2)
    paid_amount: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
    )
    status: str = Field(default="OPEN", min_length=1, max_length=20)
    description: str | None = Field(default=None, max_length=1000)


class ClaimUpdate(BaseModel):
    """Editable claim fields; generated identity and audit values are immutable."""

    policy_id: int | None = Field(default=None, gt=0)
    incident_date: ApiDate | None = None
    claim_date: ApiDate | None = None
    claim_amount: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
    )
    paid_amount: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
    )
    status: str | None = Field(default=None, min_length=1, max_length=20)
    description: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "ClaimUpdate":
        """Prevent nulls from bypassing required claim columns."""
        for field in (
            "policy_id",
            "incident_date",
            "claim_date",
            "claim_amount",
            "status",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} alanı boş bırakılamaz.")
        return self


class ClaimPolicyContext(BaseModel):
    """Policy and customer fields shown as read-only in the claims screen."""

    policy_id: int
    policy_no: str | None
    tckn_vkn: str
    product_type: str
    start_date: ApiDate
    end_date: ApiDate
    premium_amount: Money
    status: str | None
    first_name: str
    last_name: str
    email: EmailStr | None
    birth_date: ApiDate | None


class ClaimRead(BaseModel):
    """Claim representation matching the CLAIMS table."""

    claim_id: int
    claim_no: str
    policy_id: int
    incident_date: ApiDate
    claim_date: ApiDate
    claim_amount: Money
    paid_amount: Money | None
    status: str | None
    description: str | None
    created_by: str
    created_at: ApiDateTime | None


class TokenResponse(BaseModel):
    """Bearer token response returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"
