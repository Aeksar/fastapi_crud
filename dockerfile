FROM python:3.12-slim

WORKDIR /task_api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]