from django.core.management.base import BaseCommand, CommandError
import schedule, time
def job():
    print("I am working")

class Command(BaseCommand):
    help = "Runs the Scheduler for notifications"

    def handle(self, *args, **options):
        schedule.every(3).seconds.do(job)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

        