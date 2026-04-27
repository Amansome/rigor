FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev

COPY rigor/ ./rigor/

RUN useradd -m -u 1000 rigor && chown -R rigor:rigor /app
USER rigor

ENV PORT=8080
EXPOSE 8080

CMD ["uv", "run", "uvicorn", "rigor.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
