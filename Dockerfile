ARG PYTHON_VERSION=3.14

FROM ghcr.io/astral-sh/uv:latest AS uv
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=uv /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 5000

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
