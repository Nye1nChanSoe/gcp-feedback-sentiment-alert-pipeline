FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY main.py .

ENV PORT=8080

CMD ["uv", "run", "functions-framework", "--target=handle_feedback", "--host=0.0.0.0", "--port=8080"]