from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query

from order_history.exceptions import (
    AccessDeniedError,
    InvalidRequesterError,
    OrderHistoryError,
)
from order_history.models import OrderQuery, Requester, RequesterRole
from order_history.service import get_orders


def create_app(*, db_path: Path) -> FastAPI:
    """Create the order history HTTP API."""
    app = FastAPI()

    @app.get("/orders")
    def list_orders(
        customer_id: Annotated[str, Query()],
        requester_profile: Annotated[str, Header(alias="X-Requester-Profile")],
        requester_id: Annotated[str, Header(alias="X-Requester-Id")],
        order_id: Annotated[str | None, Query()] = None,
        status: Annotated[str | None, Query()] = None,
        order_date: Annotated[date | None, Query()] = None,
        page_token: Annotated[str | None, Query()] = None,
        requester_customer_id: Annotated[
            str | None, Header(alias="X-Requester-Customer-Id")
        ] = None,
    ) -> dict[str, object]:
        try:
            role = RequesterRole(requester_profile)
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail="invalid requester profile",
            ) from exc

        requester = Requester(
            id=requester_id,
            role=role,
            customer_id=requester_customer_id,
        )
        query = OrderQuery(
            customer_id=customer_id,
            order_id=order_id,
            status=status,
            order_date=order_date,
            page_token=page_token,
        )

        try:
            response = get_orders(requester, query, db_path=db_path)
        except AccessDeniedError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except InvalidRequesterError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except OrderHistoryError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return {
            "orders": response.orders,
            "total_orders_for_customer": response.total_orders_for_customer,
            "total_pages": response.total_pages,
            "next_page_token": response.next_page_token,
            "previous_page_token": response.previous_page_token,
        }

    return app
