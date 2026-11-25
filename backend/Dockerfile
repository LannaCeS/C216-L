FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY app ./app

COPY alembic.ini ./
COPY alembic ./alembic

RUN pip install --no-cache-dir poetry \
&& poetry config virtualenvs.create false \
&& poetry install --only main --no-interaction --no-ansi

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]