FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry --no-cache-dir

# Copy dependency files first (layer caching)
COPY pyproject.toml poetry.lock* ./

# Install dependencies without creating a virtualenv inside the container
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the backend code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]