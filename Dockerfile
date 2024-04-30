FROM python:3.12.3-alpine

ENV POETRY_VERSION=1.8.2

RUN pip install "poetry==$POETRY_VERSION"
ENV PYTHONPATH="$PYTHONPATH:/app"
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction --no-ansi

COPY alembic.ini prestart.sh /app/
COPY migrations /app/migrations
COPY app /app/app

ENTRYPOINT sh prestart.sh
