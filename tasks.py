# tasks.py
from celery import Celery
from celery.utils.log import get_task_logger
from get_live_games import LivescoreScraper

celery = Celery('soccer-goals')
logger = get_task_logger(__name__)
celery.config_from_object('celery_config')

