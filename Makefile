.PHONY: dev test lint typecheck check migrate ui

dev:
	uvicorn main:app --reload

ui:
	cd ui && python -m http.server 5500

migrate:
	alembic upgrade head

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy app

check: lint typecheck test
