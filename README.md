# UniReview API

Микросервисная архитектура для управления пользователями, постами и комментариями.

## 🏗 Архитектура проекта

```
project/
├── services/
│   ├── users/              # Микросервис пользователей (порт 8001)
│   ├── posts/              # Микросервис постов (порт 8002)
│   └── comments/           # Микросервис комментариев (порт 8003)
├── shared/                  # Общий код
│   ├── utils/
```

## 👥 Команда

| Разработчик | Закрепленный сервис |
|------------|-------------------|
| **Mishanyyya(dev1)** | `users` | 
| **f3n0men(dev2)** | `posts` | 
| **DaniilYakovlev-Rbk(dev3)** | `***` |

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.11+
- FastAPI
- Ruff
- Git

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Mishanyyya/PSWCS.git
```
cd project-name

# 2. Настроить виртуальное окружение (для своего сервиса)
```bash
cd services/users  # или posts/comments
python3 -m venv .venv
source venv/bin/activate  # на Windows: venv\Scripts\activate
pip install -r requirements.txt
```