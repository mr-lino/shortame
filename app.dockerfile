FROM python:3.10

WORKDIR /shortame

COPY . .

RUN pip install poetry

RUN poetry install

CMD [".venv/bin/uvicorn", "shortame.app:app", "--host", "0.0.0.0", "--port", "5000"]