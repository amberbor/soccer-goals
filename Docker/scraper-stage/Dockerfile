# Stage 4: Scraper
FROM python:3.9-slim as scraper-stage

WORKDIR /app

COPY . /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

CMD ["python", "get_live_games.py"]
