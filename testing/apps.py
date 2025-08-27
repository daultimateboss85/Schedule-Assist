from django.apps import AppConfig
import threading, os
from jobs.scheduler import scheduler

class TestingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testing'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            thread = threading.Thread(target=scheduler, daemon=True)
            thread.start()