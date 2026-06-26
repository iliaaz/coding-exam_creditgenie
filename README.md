# Python coding exam template

Fork this repo for each exam. Workflow: **spec → rename → tests → implement → check**.

## Intended way of working

### Setup

```bash
uv sync --dev
```

Confirm the exam environment supports the Python version in `.python-version`. To change it, update `.python-version`, `requires-python` in `pyproject.toml`, and `[tool.ruff]` / `[tool.ty]` target versions, then run `uv sync --dev`.

Optional: install pre-commit hooks after sync:

```bash
uv run pre-commit install
```

### Workflow

1. **Fork** — fork on GitHub and clone your fork.
2. **Spec** — fill in `SPEC.md` from the exam prompt before writing code.
3. **Rename** — rename the package and test files to match the problem (`snake_case`):

   ```bash
   git mv solution <package>
   git mv tests/unit/test_unit.py tests/unit/test_<package>.py
   git mv tests/integration/test_integration.py tests/integration/test_<package>_integration.py
   ```

   Then update all of the following:

   - [ ] `pyproject.toml` → `[tool.hatch.build.targets.wheel] packages = ["<package>"]`
   - [ ] `pyproject.toml` → `[project] name = "<package>"` (optional but tidy)
   - [ ] Test imports → `from <package> import ...`
   - [ ] Run `uv sync --dev` to reinstall the package

4. **Tests** — write unit tests in `tests/unit/` from `SPEC.md` scenarios (positive and negative cases). Add integration tests for critical flows. Run `uv run pytest -v`.
5. **Implement** — code in `<package>/` until all tests pass. Export the public API from `__init__.py`. Split into modules (e.g. `models.py`, `service.py`) when the feature outgrows a single file.
6. **Check** — run `./scripts/check.sh` before submitting.
7. **Push** — optional; CI runs the same checks as `./scripts/check.sh`.

Work in that order. Do not skip the spec or tests.

### Time-boxing

Under pressure, ship **must haves** first. Only pick up **nice to haves** if must haves and tests are green. Respect **won't do** — do not expand scope.

## Project layout

| Path | Purpose |
|------|---------|
| `SPEC.md` | Design spec |
| `solution/` | Package placeholder — rename to `<package>/` |
| `tests/unit/` | Unit tests — positive and negative cases |
| `tests/integration/` | Integration tests — critical cross-boundary flows |
| `tests/conftest.py` | Shared fixtures |
| `tests/README.md` | How scenarios map to unit and integration tests |
| `.vscode/settings.json` | Format on save, pytest discovery |
| `.pre-commit-config.yaml` | Optional ruff hooks on commit |
| `.python-version` | Python version for uv |
| `pyproject.toml` | Project config and tool settings |
| `scripts/check.sh` | Lint, format, type-check, and test |
| `AGENTS.md` | AI assistant instructions |
| `.cursor/rules/exam-workflow.mdc` | Always-on exam workflow for Cursor |
| `.github/workflows/ci.yml` | CI quality gate |

## Adding dependencies

Runtime libraries (e.g. `pydantic`, `httpx`, `sqlalchemy`):

```bash
uv add <package>
```

Dev-only tools:

```bash
uv add --dev <package>
```

## Commands

| Command | Does |
|---------|------|
| `uv sync --dev` | Install dependencies |
| `uv run pytest tests/unit -v` | Unit tests only |
| `uv run pytest tests/integration -v` | Integration tests only |
| `uv run pytest -v` | All tests |
| `./scripts/check.sh` | Lint, format, type-check, and test |
| `uv run pre-commit run --all-files` | Run pre-commit hooks manually |

## Why some things look duplicated

| Pair | Why both exist |
|------|----------------|
| `README.md` + `AGENTS.md` | README for you; AGENTS.md for the AI |
| `./scripts/check.sh` + GitHub CI | Local check before submit; CI on push |
| `./scripts/check.sh` + pre-commit | Full gate before submit; fast checks on commit |

## Tooling

[uv](https://docs.astral.sh/uv/) · [ruff](https://docs.astral.sh/ruff/) · [ty](https://docs.astral.sh/ty/) · [pytest](https://docs.pytest.org/) · [pre-commit](https://pre-commit.com/)
