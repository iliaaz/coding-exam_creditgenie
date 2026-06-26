# Agent instructions

Spec-driven, test-driven workflow for this exam repo.

1. Read `SPEC.md` before changing code.
2. Rename `solution/`, `tests/unit/test_unit.py`, and `tests/integration/test_integration.py` to match the problem (`snake_case`). Update `pyproject.toml` `packages`, test imports, and optionally `[project] name`. Run `uv sync --dev`.
3. Write unit tests in `tests/unit/` — one test per scenario. Include **positive and negative** cases as ordinary pytest functions; do not use a separate inverse framework.
4. Write integration tests in `tests/integration/` for critical cross-boundary flows.
5. Implement in `<package>/` until **all unit and integration tests pass**. Export public API from `__init__.py`. Respect won't-do boundaries.
6. Run `./scripts/check.sh` before finishing.

Conventions:

- Do not declare implementation complete while any test is failing
- Tests import the public API: `from <package> import ...`
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`
- Prioritize must haves over nice to haves when time is limited
- Python 3.14+ type hints; no `from __future__ import annotations`
- Tooling: uv, ruff, ty, pytest

Runtime deps: `uv add <package>`. Dev deps: `uv add --dev <package>`.
