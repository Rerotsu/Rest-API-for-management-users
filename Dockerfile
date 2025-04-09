
    FROM python:3.12-slim AS builder


    ENV POETRY_VERSION=2.1.2
    RUN pip install "poetry==${POETRY_VERSION}"
    
    WORKDIR /app
    
    COPY poetry.lock pyproject.toml ./
    
    RUN poetry config virtualenvs.create false && \
        poetry install --no-interaction --no-ansi --only main --no-root
    
    FROM python:3.12-slim
    
    WORKDIR /app
    
    COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
    COPY --from=builder /usr/local/bin /usr/local/bin
    
    COPY ./src ./src
    COPY .env ./.env
    
    EXPOSE 8000
    
    CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
    