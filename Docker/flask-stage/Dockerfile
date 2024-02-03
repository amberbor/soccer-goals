# Stage 2: Flask
FROM python:3.9-slim as flask-stage

WORKDIR /app

COPY . /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


# defining env vars
ENV FLASK_APP=app.py
# watch app' files
ENV FLASK_DEBUG=true
ENV FLASK_ENV=development

EXPOSE 5000

CMD sleep 10 && flask db upgrade ; python3 -m flask run --host=0.0.0.0