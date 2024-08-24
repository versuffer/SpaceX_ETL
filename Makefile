install:
	sudo apt install pre-commit
	pip install poetry
	poetry install --no-root --no-interaction --with dev

check:
	isort . --check-only
	flake8
	mypy .
	bandit -c pyproject.toml -r .

format:
	isort .
	black .
	flake8
