# FastAPI CRUD

## Описание

Проект демонстрирует базовые операции с данными, включая создание, чтение, обновление и удаление записей.

## Основные возможности

- **Создание записей**: Добавление новых данных через POST-запросы.
- **Чтение данных**: Получение списка или конкретной записи через GET-запросы.
- **Обновление записей**: Изменение существующих данных с помощью PUT или PATCH-запросов.
- **Удаление записей**: Удаление данных через DELETE-запросы.
- Быстрая и асинхронная обработка запросов благодаря FastAPI.
- Поддержка валидации данных и автоматическая генерация документации API (Swagger/ReDoc).

## Зависимости

- Python 3.8+
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

3. Настройте подключение к базе данных, указав в файле .env следущие переменные:
   - DB_HOST
   - DB_PORT
   - DB_USER
   - DB_PASSWORD
   - DB_NAME
   - TEST_DB_HOST
   - TEST_DB_NAME

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
