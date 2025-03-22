FROM python:3.13-slim-bookworm

ENV POETRY_VERSION=2.1.1

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /app

COPY . ./

RUN poetry install --without dev

ENTRYPOINT ["poetry", "run", "python", "-m", "ytdl_nfo"]