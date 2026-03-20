# services/review/Makefile (Windows-версия)

# Переменные для Windows
SERVICE_NAME=reviews
PORT=8002
PYTHON=python
VENV=venv
PIP=$(VENV)\Scripts\pip
PYTHON_VENV=$(VENV)\Scripts\python

# Цвета для Windows (убираем ANSI-коды, они не работают)
GREEN := 
RED := 
NC := 

.PHONY: help install run dev migrate seed test lint format clean env init

help: ## Показать помощь
	@echo === $(SERVICE_NAME) Service ===
	@echo Доступные команды:
	@echo   make install - Установка зависимостей
	@echo   make run     - Запуск сервиса
	@echo   make dev     - Запуск в режиме разработки
	@echo   make seed    - Заполнение тестовыми данными
	@echo   make format  - Форматирование кода
	@echo   make lint    - Проверка кода
	@echo   make clean   - Очистка

install: ## Установка зависимостей
	@echo Установка зависимостей...
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo Готово!

run: ## Запуск сервиса (без авто-перезагрузки)
	$(PYTHON_VENV) -m uvicorn app.main:app --host localhost --port $(PORT)

dev: ## Запуск в режиме разработки (с авто-перезагрузкой)
	@echo Запуск $(SERVICE_NAME) в режиме разработки...
	$(PYTHON_VENV) -m uvicorn app.main:app --reload --host localhost --port $(PORT)

seed:
	@echo Заполнение базы тестовыми данными...
	$(PYTHON_VENV) -m app.seeds.run_seeder

lint: ## Проверка кода
	@echo Проверка кода...
	$(PYTHON_VENV) -m ruff check app/ --fix

format: ## Форматирование кода
	@echo Форматирование кода...
	$(PYTHON_VENV) -m ruff check app/ --fix
	$(PYTHON_VENV) -m ruff format app/

clean: ## Очистка временных файлов
	@echo Очистка...
	if exist $(VENV) rmdir /s /q $(VENV)
	if exist __pycache__ rmdir /s /q __pycache__
	del /s /q *.pyc 2>nul

env: ## Создать .env из .env.example
	@if not exist .env copy .env.example .env

init: env install seed ## Полная инициализация
	@echo Готово!