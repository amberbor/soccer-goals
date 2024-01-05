from celery import Celery
from get_m3u8 import LivestreamCapturer

# Create a Celery instance
celery = Celery(
    'get_live_games',
    broker='redis://localhost:6379/0',  # Redis URL
    backend='redis://localhost:6379/0',  # Redis URL
    include=['get_live_games']  # Import path to your script
)
# Optional configuration
celery.conf.update(
    result_expires=3600,  # Result expires in 1 hour
)
