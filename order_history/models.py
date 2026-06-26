from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class RequesterRole(StrEnum):
    CUSTOMER = "customer"
    SUPPORT_AGENT = "support_agent"


@dataclass(frozen=True, slots=True)
class Requester:
    id: str
    role: RequesterRole
    customer_id: str | None = None


@dataclass(frozen=True, slots=True)
class OrderQuery:
    customer_id: str
    order_id: str | None = None
    status: str | None = None
    order_date: date | None = None
    page_token: str | None = None
    page_size: int = 50


@dataclass(frozen=True, slots=True)
class OrderListResponse:
    orders: list[dict[str, object]]
    total_orders_for_customer: int
    total_pages: int
    next_page_token: str | None
    previous_page_token: str | None


CUSTOMER_VISIBLE_FIELDS = frozenset(
    {"status", "total", "items", "created_at", "delivered_at"}
)

SUPPORT_ONLY_FIELDS = frozenset({"id", "customer_id", "refund_reason", "note"})
