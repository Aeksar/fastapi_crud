FROM python:3.12-slim

WORKDIR /task_api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN alembic upgrade head

CMD [ "python", "main.py" ]