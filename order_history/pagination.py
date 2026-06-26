def decode_page_offset(page_token: str | None) -> int:
    if page_token is None:
        return 0
    return int(page_token)


def encode_page_token(offset: int) -> str:
    return str(offset)


def page_tokens(
    *,
    offset: int,
    page_size: int,
    total_items: int,
) -> tuple[str | None, str | None]:
    next_token = None
    if offset + page_size < total_items:
        next_token = encode_page_token(offset + page_size)

    previous_token = None
    if offset > 0:
        previous_token = encode_page_token(max(offset - page_size, 0))

    return next_token, previous_token


def total_pages(total_items: int, page_size: int) -> int:
    if total_items == 0:
        return 1
    return (total_items + page_size - 1) // page_size
