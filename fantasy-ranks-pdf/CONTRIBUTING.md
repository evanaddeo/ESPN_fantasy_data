# Contributing

Thanks for your interest in contributing!

## Development setup
1. Install Python 3.11+.
2. Clone the repo and install with dev extras:
   ```bash
   python -m pip install -U pip
   pip install -e .[dev]
   pre-commit install
   ```

## Running checks
```bash
ruff check .
ruff format --check .
black --check .
mypy
pytest -q
```

## Tests
- Unit tests live under `tests/`.
- Integration tests are marked `@pytest.mark.integration` and are skipped by default.

## Pull requests
- Keep changes focused and include tests when adding features or fixing bugs.
- Follow the existing code style and type hints.
