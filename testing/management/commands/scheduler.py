from django.core.management.base import BaseCommand, CommandError
import schedule, time
from ._jobs import job


class Command(BaseCommand):
    help = "Runs the Scheduler for notifications"

    def handle(self, *args, **options):
        
        def scheduler():
            schedule.every(5).seconds.do(job)
            #schedule.every().hour.at(":00").do(job)

            while True:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler()
    