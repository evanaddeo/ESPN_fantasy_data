install:
	python -m pip install -U pip
	pip install -e .[dev]

lint:
	ruff check .
	ruff format --check .
	black --check .
	mypy

test:
	pytest -q

fmt:
	ruff check --fix .
	ruff format .
	black .
