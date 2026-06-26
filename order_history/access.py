from order_history.exceptions import AccessDeniedError, InvalidRequesterError
from order_history.models import Requester, RequesterRole


def verify_requester_access(requester: Requester, customer_id: str) -> None:
    """Ensure the requester may query orders for the given customer."""
    if requester.role == RequesterRole.SUPPORT_AGENT:
        return

    if requester.role != RequesterRole.CUSTOMER:
        raise InvalidRequesterError(f"unsupported requester role: {requester.role}")

    if requester.customer_id is None:
        raise InvalidRequesterError("customer requester must include customer_id")

    if requester.customer_id != customer_id:
        raise AccessDeniedError(
            f"customer {requester.customer_id!r} cannot access orders "
            f"for {customer_id!r}"
        )
