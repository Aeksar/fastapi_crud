# FastAPI CRUD

## Описание

Проект выдает базу.

## Основные возможности

- Удаление, обновление, создание, чтение данных о задачах и пользователях
- Аутентификация на основе JWT, а также возможность подключения двухфакторки
- Кэширование запросов при помощи Redis
- Настроенный CI в Github Actions.

## Зависимости

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- Pytest

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Aeksar/fastapi_crud.git
   cd fastapi_crud
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте подключение к PostgreSQL и Redis, указав в файле .env следущие переменные:
   - DB_HOST
   - DB_PORT
   - DB_USER
   - DB_PASSWORD
   - DB_NAME
   - TEST_DB_HOST
   - TEST_DB_NAME
  
   - REDIS_PORT
   - REDIS_HOST
   - REDIS_PASSWORD
   - REDIS_USERNAME
   - REDIS_DB

4. Примените миграции:
   ```bash
     alembic upgrade head
   ```

5. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```
   или
   ```bash
   python main.py
   ```

## Альтернативная установка (Docker)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Aeksar/fastapi_crud.git
   cd fastapi_crud
   ```

2. Запустите docker compose файл:
   ```bash
   docker compose up --build
   ```

## Использование

После запуска сервера API будет доступно по адресу `http://localhost:8000`. Вы можете:

- Просмотреть интерактивную документацию API по адресу `http://localhost:8000/docs` (Swagger) или `http://localhost:8000/redoc` (ReDoc).
- Отправлять запросы для выполнения операций CRUD через HTTP-клиенты (например, `curl`, Postman или любой другой инструмент).

Пример запроса для получения списка записей:
```bash
curl -X GET "http://localhost:8000/tasks/"
```
