FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN apt-get update \
    && apt-get install -y build-essential \
    && pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry config virtualenvs.create false \
    && poetry add python-jose\
    && poetry add aioredis\
    && poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN apt-get update \
    && apt-get install -y build-essential \
    && pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN pip install alembic

RUN pip install asyncpg

COPY ./app /code/app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
