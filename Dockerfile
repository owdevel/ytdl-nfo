# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim AS build

WORKDIR /app

# Upgrade pip and install poetry
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install poetry

COPY . .

# Build the app
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install && poetry build


ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the wheel file(s) from the build stage
COPY --from=build /app/dist/*.whl ./

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install *.whl

# Run the application.
ENTRYPOINT [ "ytdl-nfo" ]
