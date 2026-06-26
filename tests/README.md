# Tests

## Unit tests

Write standard pytest functions in `tests/unit/`. For each feature area in `SPEC.md`, include **positive and negative** cases — same style, same file, no separate framework.

```python
@pytest.mark.unit
def test_creates_order_with_valid_items() -> None:
    ...

@pytest.mark.unit
def test_rejects_empty_items() -> None:
    ...
```

Each `SPEC.md` scenario (GIVEN / WHEN / THEN) maps to one unit test.

## Integration tests

Write in `tests/integration/` for flows that cross boundaries (DB, HTTP, filesystem).

## Layout

| Path | Purpose |
|------|---------|
| `unit/` | Unit tests — positive and negative |
| `integration/` | Cross-boundary flows |
| `conftest.py` | Shared fixtures |

## Commands

```bash
uv run pytest tests/unit -v
uv run pytest tests/integration -v
uv run pytest -v
```
