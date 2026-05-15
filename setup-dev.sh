#!/usr/bin/env bash
# ─── Установка git-хуков и зависимостей для разработки ───────────────────────
set -euo pipefail

echo "📦 Настройка git-хуков..."
git config core.hooksPath .githooks
echo "✔  git-хуки подключены из .githooks/"

cd services/users
pip install -r requirements.txt 

echo ""
echo " Готово! Хуки активны:"
echo "   - pre-commit  → ruff lint + тесты"
echo "   - commit-msg  → Conventional Commits"
echo "   - pre-push    → тесты + coverage ≥ 70%"

#ВОТ ЭТО ПЕРЕПИСАТЬ ЭТО ВАЩЕ ЧУШЬ