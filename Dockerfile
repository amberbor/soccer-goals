## Base stage
#FROM node:14 as base-stage
#
#WORKDIR /app
#
#COPY . /app
#
## Install dependencies
#WORKDIR /app/frontend
#RUN npm install
#
## Build the React app
#RUN npm run build
#
## Final stage
#FROM python:3.9-slim as final-stage
#
#ARG UID=10001
#RUN adduser \
#    --disabled-password \
#    --gecos "" \
#    --home "/nonexistent" \
#    --shell "/sbin/nologin" \
#    --no-create-home \
#    --uid "${UID}" \
#    appuser
#
#WORKDIR /app
#
#COPY --from=base-stage /app /app
#
## Install additional Python dependencies if needed
#RUN pip install --upgrade pip && pip install -r requirements.txt
#
## Set environment variables
#ENV FLASK_APP=app.py
#ENV FLASK_DEBUG=true
#ENV FLASK_ENV=development
#
#EXPOSE 5000
#
#
## Command to run both Flask app and get_live_games.py
#CMD flask db upgrade; python3 -m flask run --host=0.0.0.0 & python3 get_live_games.py
