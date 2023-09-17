FROM python:3.10

WORKDIR /shortame

COPY . .

RUN pip install poetry

RUN poetry install

CMD [".venv/bin/python", "key_generator.py"]