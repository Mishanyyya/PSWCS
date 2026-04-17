PYTHON ?= python3
VENV ?= .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_BIN := $(VENV_BIN)/python
UVICORN := $(VENV_BIN)/uvicorn
ALEMBIC := $(VENV_BIN)/alembic

HOST ?= 127.0.0.1
PORT ?= 8001
SEED_COUNT ?= 25
SEED_FORCE ?=
SEED_OUTPUT_FILE ?= users_credentials.txt

.PHONY: help venv install clean-venv recreate-venv lint migrate migrate-down seed run bootstrap up

help:
	@echo "Available targets:"
	@echo "  make venv           - Create virtual environment"
	@echo "  make install        - Install runtime and dev dependencies"
	@echo "  make clean-venv     - Remove virtual environment"
	@echo "  make recreate-venv  - Recreate virtual environment from scratch"
	@echo "  make lint           - Run ruff checks"
	@echo "  make migrate        - Apply alembic migrations"
	@echo "  make migrate-down   - Roll back last alembic migration"
	@echo "  make seed           - Generate test users"
	@echo "  make run            - Run FastAPI service"
	@echo "  make bootstrap      - Full setup (venv + install + migrate + seed)"
	@echo "  make up             - One command to bootstrap and run service"

venv:
	@test -d "$(VENV)" || $(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt

clean-venv:
	rm -rf $(VENV)

recreate-venv: clean-venv install

lint: install
	$(VENV_BIN)/ruff check app seed_users.py

migrate: install
	$(ALEMBIC) upgrade head

migrate-down: install
	$(ALEMBIC) downgrade -1

seed: install
	$(PYTHON_BIN) seed_users.py $(SEED_COUNT) $(SEED_FORCE) --output "$(SEED_OUTPUT_FILE)"

run: install
	$(UVICORN) app.main:app --host $(HOST) --port $(PORT) --reload

bootstrap: install migrate seed

up: bootstrap run
