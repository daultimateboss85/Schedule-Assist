import schedule, time
from jobs.jobs import job


def scheduler():
        #schedule.every(5).seconds.do(job)
        #schedule.every().hour.at(":00").do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)