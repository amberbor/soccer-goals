# Stage 1: Celery
FROM python:3.9-slim as celery-stage

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y gcc pkg-config default-libmysqlclient-dev

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER appuser
