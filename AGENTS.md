# AGENTS.md

## Project Overview

mgallery is an image deduplication script that helps identify and manage duplicate images. It scans directories, extracts EXIF/metadata, computes perceptual hashes (phash), and provides tools for comparing, renaming, and managing duplicate images.

## Project Structure

- `mgallery/mgallery.py`: Main entry point
- `mgallery/compare.py`: Image comparison logic using perceptual hashing
- `mgallery/scanner.py`: Directory scanning and file discovery
- `mgallery/image.py`: Image metadata extraction (EXIF)
- `mgallery/phash.py`: Perceptual hash computation
- `mgallery/thumbnails.py`: Thumbnail generation
- `mgallery/database.py`: SQLite database for caching
- `mgallery/rename.py`: File renaming utilities
- `mgallery/resort.py`: Reorganize images by date
- `mgallery/autodelete.py`: Auto-delete duplicates
- `mgallery/settings.py`: Configuration and environment variables
- `mgallery/date_re.py`: Date regex patterns
- `mgallery/utils.py`: Helper utilities

## Development Commands

```bash
# Install dependencies
uv sync --all-extras --dev

# Run linting and type checking
uv run ruff check .
uv run ty check
uv run pre-commit run --all-files

# Run tests
make test
uv run pytest tests/

# Run the script
mgallery --help
```

## Language & Environment

- Python >=3.13, <3.14 (see `pyproject.toml`)
- Follow PEP 8 style guidelines, with Ruff enforcing style (120 char line length)
- Use type hints for public functions and complex code paths
- Use only f-strings for string formatting (never `.format()` or `%` formatting)
- Use list/dict/set comprehensions instead of `map`/`filter` where it improves readability
- Prefer `pathlib.Path` over `os.path` for filesystem paths
- Follow PEP 257 for docstrings where docstrings are used

## Code Style & Tooling

Configured in `pyproject.toml`:

- **Ruff** for linting and import management (`[tool.ruff]`, `[tool.ruff.lint]`)
- **Bandit** for basic security checks (`[tool.bandit]`)
- **ty** for type checking
- **pre-commit** is used to run the tools before commits

Run manually:

```bash
uv run pre-commit run --all-files
uv run ruff check .
uv run ty check
uv run bandit -c pyproject.toml .
```

## Code Conventions

**Naming** (ruff N enforces most):
- Modules: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`; private prefixed `_`
- Constants: `UPPER_SNAKE_CASE`; env-driven ones live in `mgallery/settings.py`

**Architecture**:
- Keep modules focused: one responsibility per file
- Pure functions preferred for business logic
- I/O operations separated from processing logic

**Do NOT use**:
- `print()` for output (use logging or rich for UI)
- PEP 585 typing (`Tuple[X]/Optional[X]/List[X]/Dict[X]` — use PEP 604 `X | None` / `list[X]`)
- Mutable default arguments
- Inline comments and emojis in code

## Testing Guidelines

- Use `pytest` for tests
- Tests live in `tests/` directory
- Run with `make test` or `uv run pytest tests/`

## Dependencies

**Core**: pillow, rawpy, numpy, exifread, pycairo, PyGObject, redis
**Development**: pytest, ipython, pre-commit, ty, bandit

## Security Guidelines

- Never commit secrets, passwords, or API tokens
- Configure sensitive values via environment variables
- Run `bandit` periodically or in CI
- Validate any external input before using it in system calls

## AI Behavior

Response style -- concise and minimal:

- Provide minimal, working code without unnecessary explanation
- Omit comments unless essential for understanding
- Skip boilerplate and obvious patterns unless requested
- Use type inference and shorthand syntax where possible
- Prefer the core solution, skip tangential suggestions
- Assume familiarity with language idioms and patterns
- Let code speak for itself through clear naming and structure
- Avoid over-explaining standard patterns and conventions
- Provide just enough context to understand the solution
- Trust the developer to handle obvious cases independently
