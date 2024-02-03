# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy the built artifacts from each stage
COPY --from=celery-stage /app /app
COPY --from=flask-stage /app /app
COPY --from=react-stage /app /app
COPY --from=scraper-stage /app /app