# my_app/tasks.py
from celery import shared_task
from datetime import datetime

@shared_task
def print_time_task():
    """A simple task to demonstrate Celery Beat cron job functionality."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Celery Beat Cron Job Ran At: {current_time}")
    return True