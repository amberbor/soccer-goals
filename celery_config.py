# celeryconfig.py

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
timezone = 'UTC'
track_started = True
result_expires = 7200
task_serializer = 'json'
worker_pool = 'prefork'
result_serializer = 'json'
worker_concurrency = 4