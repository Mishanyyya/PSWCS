
SERVICE_NAME=reviews
PORT=8002
PYTHON=python
VENV=venv
PIP=$(VENV)\Scripts\pip
PYTHON_VENV=$(VENV)\Scripts\python

# зависимости (не алкогольные)
install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt


run: ## Запуск сервиса
	$(PYTHON_VENV) -m uvicorn app.main:app --host localhost --port $(PORT)

seed:
	$(PYTHON_VENV) -m app.seeds.run_seeder

lint: ## линтер
	$(PYTHON_VENV) -m ruff check app/ --fix
	$(PYTHON_VENV) -m ruff format app/
