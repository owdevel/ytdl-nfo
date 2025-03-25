# https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
FROM python:3.13-slim-bookworm as build

# Poetry version
ENV POETRY_VERSION=2.1.1

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy only pyproject.toml and poetry.lock first to install dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies and remove Poetry cache afterward
RUN poetry install --without dev --no-interaction --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.13-slim-bookworm as run

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ytdl_nfo ./ytdl_nfo

ENTRYPOINT ["python", "-m", "ytdl_nfo"]