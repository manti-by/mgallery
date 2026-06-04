# AGENTS.md

## Project Overview

Image deduplication script. Scans directories, computes perceptual hashes (OpenCV), and identifies duplicates via PostgreSQL.

## Architecture

Entry point: `mgallery.py` (root) — dispatches CLI flags to service runners.

```
mgallery/
  library/      # Data layer: SQLAlchemy models, DB access, image processing, phash
  services/     # Business logic: scanner, compare, autodelete, rename, resort, thumbnails, dump
  utils/        # Settings, date regex, filesystem helpers
```

- **Database**: PostgreSQL via SQLAlchemy 2.x (raw `text()` queries, not ORM). Alembic for migrations.
- **Models**: `mgallery/library/tables.py` (single `Image` table). `Base` is exported from there for Alembic.
- **DB access**: `mgallery/library/database.py` — `Database` class wraps engine + session factory.
- **Type checker**: `ty` (not mypy/pyright). Pyright is disabled in `opencode.json`.
- **Image processing**: `rawpy` for RAW (arw/dng), `cv2` (OpenCV) for RGB. `cv2` import is TYPE_CHECKING-guarded.

## Development Commands

```bash
uv sync --all-extras --dev          # install deps
make test                           # uv run pytest tests/
make check                          # git add . && ty check && pre-commit run
make migrate                        # uv run alembic upgrade head
uv run mgallery.py -s               # scan
uv run mgallery.py -c               # compare
```

Pre-commit runs: pyupgrade (`--py313-plus`), ruff (`--fix`), ruff-format, bandit. CI only runs pre-commit — tests and `ty check` are **not** in CI.

## Environment

Required env vars (see `mgallery/utils/settings.py`):
- `GALLERY_PATH` — image root directory
- `DATABASE_URL` — PostgreSQL connection string
- `THUMBNAILS_PATH` — thumbnail output directory

System deps: `libraw-dev`, `python3-gi`, `gir1.2-gtk-3.0`, `libcairo2-dev` (for rawpy + PyGObject).

## Testing

Tests use SQLite in-memory (`tests/conftest.py` — `create_test_engine()`), not PostgreSQL. Pass the test engine to `Database(engine=...)`.

## Git Workflow

This project adheres strictly to the Git Flow branching model. AI agents must follow these guidelines:

### Main Branch:

- The `master` branch always contains production-ready, stable code.
- Never commit directly to `master`.
- Do not use `git push --force` on the `master` branch.
- Do not merge branches into `master` without explicit approval.

### Feature Branches:

- Create feature branches using the naming convention `<agent-name>/feature/<descriptive-name>` (e.g., `opencode/feature/add-thumbnail-cache`).
- Use the [Conventional Commits](https://www.conventionalcommits.org) specification for commit messages (e.g., `feat:`, `fix:`, `docs:`).
- Ensure all local tests pass before committing.
- Use `git push --force-with-lease` if needed on your feature branch, but never on `master`.

### Pull Requests (PRs):

- Open a Pull Request for every completed feature branch.
- PRs must be reviewed and pass all CI checks before merging.
- The PR title should follow the Conventional Commits specification.

## Conventions

- Python 3.13 only. Use PEP 604 unions (`X | None`), not `Optional[X]`.
- ruff isort has custom section order: `mgallery` → `mgallery.library` → `mgallery.utils` → `mgallery.services` (see `pyproject.toml`).
- Use only f-strings for string formatting (never `.format()` or `%` formatting).
- Use list/dict/set comprehensions instead of `map`/`filter` where it improves readability.
- Prefer `pathlib.Path` over `os.path` for filesystem paths.
- Use only named arguments instead of positional arguments in function and method calls.
- No `print()` — use `logging`.
- No inline comments or emojis in code.
- No mutable default arguments (use `field(default_factory=...)`).
- `make check` runs `git add .` before linting — be aware when staging is incomplete.

## Database Migrations

When creating Alembic migrations:

- Use descriptive names in snake_case (e.g., `add_phash_index`, `drop_legacy_columns`, `create_image_metadata_table`)
- Prefix with operation type: `add_`, `create_`, `drop_`, `alter_`, `remove_`, `rename_`
- Include the table name and what changed
- Example: `uv run alembic revision --autogenerate -m "add_image_size_column"`
