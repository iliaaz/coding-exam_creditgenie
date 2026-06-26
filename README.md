# Order history API

A minimal FastAPI service backed by SQLite for querying customer order history. Customers see a limited field set for their own orders; support agents can query any customer and see full order details.

Design details live in [`SPEC.md`](SPEC.md). Example response shape is in [`sample_output.json`](sample_output.json).

## Requirements

- Python 3.14+ (see `.python-version`)
- [uv](https://docs.astral.sh/uv/) for environment and dependency management

## Setup

```bash
uv sync --dev
```

Optional pre-commit hooks:

```bash
uv run pre-commit install
```

## Project structure

```
order_history/          # Application package
  __init__.py           # Public API exports
  api.py                # FastAPI app and GET /orders endpoint
  main.py               # CLI entry point (uvicorn server)
  service.py            # get_orders — orchestrates access, query, pagination
  access.py             # Requester authorization (customer vs support agent)
  repository.py         # SQLite queries and filters
  database.py           # Schema creation and seed loading
  seed_data.py          # Generated seed orders (500 customers, cust_42 has 847)
  models.py             # Requester, OrderQuery, OrderListResponse
  pagination.py         # Page tokens and total page calculation
  exceptions.py         # AccessDeniedError, InvalidRequesterError

tests/
  unit/                 # Service-layer tests (positive and negative)
  integration/          # HTTP + database end-to-end tests
  conftest.py           # Fixtures, test clients, requester headers

SPEC.md                 # Design spec and acceptance criteria
sample_output.json      # Example order response for cust_42
scripts/check.sh        # Lint, format, type-check, and test
```

### How it fits together

1. **`GET /orders`** (`api.py`) reads query params and requester headers, builds a `Requester` and `OrderQuery`, and calls `get_orders`.
2. **`get_orders`** (`service.py`) checks access, queries SQLite, paginates results, and shapes the response by role.
3. **`init_database`** (`database.py`) creates the `orders` table and loads rows from `seed_data.SEED_ORDERS`.
4. On startup, **`main.py`** initializes the database (if empty) and runs uvicorn.

### Requester headers

The API uses headers as a stand-in for authentication (per spec, no real auth):

| Header | Purpose |
|--------|---------|
| `X-Requester-Profile` | `customer` or `support_agent` |
| `X-Requester-Customer-Id` | Required for customers — must match `customer_id` query param |
| `X-Requester-Id` | Caller identity (e.g. `user_42`, `agent_1`) |

Query parameters:

| Param | Required | Description |
|-------|----------|-------------|
| `customer_id` | Yes | Whose orders to fetch |
| `order_id` | No | Filter to a single order |
| `status` | No | Filter by status (`completed`, `refunded`, etc.) |
| `order_date` | No | Filter by order date (`YYYY-MM-DD`) |
| `page_token` | No | Offset token from a previous response |

Customers receive: `status`, `total`, `items`, `created_at`, `delivered_at`.  
Support agents receive all fields, including `id`, `customer_id`, `refund_reason`, and `note`.

## Launch the API

```bash
uv run order-history-api
```

Defaults: `http://127.0.0.1:8000`, database at `orders.db`.

Options:

```bash
uv run order-history-api --host 0.0.0.0 --port 8000 --db-path orders.db
```

### Example requests

**Customer** — own orders, limited fields:

```bash
curl "http://127.0.0.1:8000/orders?customer_id=cust_42" \
  -H "X-Requester-Profile: customer" \
  -H "X-Requester-Customer-Id: cust_42" \
  -H "X-Requester-Id: user_42"
```

**Support agent** — any customer, full fields, with filters:

```bash
curl "http://127.0.0.1:8000/orders?customer_id=cust_42&status=completed&order_date=2026-03-15" \
  -H "X-Requester-Profile: support_agent" \
  -H "X-Requester-Id: agent_1"
```

**Pagination** — use `next_page_token` from the response:

```bash
curl "http://127.0.0.1:8000/orders?customer_id=cust_42&page_token=50" \
  -H "X-Requester-Profile: support_agent" \
  -H "X-Requester-Id: agent_1"
```

A customer requesting another customer's data returns **403 Forbidden**.

## Test

```bash
uv run pytest -v                  # all tests
uv run pytest tests/unit -v       # unit tests only
uv run pytest tests/integration -v  # integration tests only
```

Full quality gate (lint, format, types, tests):

```bash
./scripts/check.sh
```

Tests import the public API only:

```python
from order_history import get_orders, create_app, init_database
```

Integration tests use `fastapi.testclient.TestClient` against a temporary SQLite database seeded on each run.

## Public API

Exported from `order_history`:

| Symbol | Description |
|--------|-------------|
| `get_orders(requester, query, db_path=...)` | Core service function |
| `create_app(db_path=...)` | FastAPI application |
| `init_database(db_path)` | Create schema and load seed data |
| `Requester`, `OrderQuery`, `OrderListResponse` | Data types |
| `RequesterRole` | `customer` / `support_agent` |
| `AccessDeniedError`, `InvalidRequesterError` | Error types |

## Tooling

[uv](https://docs.astral.sh/uv/) · [ruff](https://docs.astral.sh/ruff/) · [ty](https://docs.astral.sh/ty/) · [pytest](https://docs.pytest.org/) · [FastAPI](https://fastapi.tiangolo.com/)

| Command | Does |
|---------|------|
| `uv sync --dev` | Install dependencies |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `uv run ty check` | Type check |
| `uv run pytest -v` | Run tests |
| `./scripts/check.sh` | All of the above |
