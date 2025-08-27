# get all events that are important and are in the next hour
# set up a scheduler for each of them

# so eg if the time is 3:30
# get all events from 4:30 to 5:30 and are today
# set a scheduler for them

# take care of what if time is 22:30. 23:30
import requests, datetime, threading, schedule


def job():
    from testing.models import DailyEvent, User
    from django.db.models import F

    def notify(event):
        """
        get current date 
        if event start time hour is not 0 notification time is easily just same as event start time -1 hour
        else subtract 1hour
        """
        owner: User = event.schedule.calendar.owner

        #for not the delta is fixed to 1 hour 
        #in future i might make the user able to set this
        time_delta_from_notification = datetime.timedelta(hours=1)

        current_date = datetime.datetime.now()
        start_time_of_event = event.start_time

        if event.start_time.hour != 0:
            event_date_time = datetime.datetime(
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                hour=start_time_of_event.hour,
                minute=start_time_of_event.minute,
            )
        else:
            one_day = datetime.timedelta(days=1)
            next_day = current_date + one_day
            next_day.hour = start_time_of_event.hour
            next_day.minute = start_time_of_event.minute

            event_date_time = next_day

        
        notification_date_time = event_date_time - time_delta_from_notification
        notification_time = notification_date_time.time()

        #print(notification_time.hour, notification_time.minute)

        # set up a thread with the job of sending the notification
        def schedule_notification(event):
            response = requests.post(
                f"https://ntfy.sh/{owner.username}{owner.id}",
                data=f"{event.title} starts soon",
            )
            #print(response.status_code)

            return schedule.CancelJob

        schedule.every().day.at(
            f"{notification_time.hour:02}:{notification_time.minute:02}"
        ).do(schedule_notification, event=event)

    def actual_job():
        """
        this job will be run at the 0th minute of each hour
        this gets the current date and time
        filters for all important events that satisfy
               current_time + 1h < event_start_time < current_time + 1h59min
        also filters for only those that are on a last viewed calendar (so we are only sending messages to events on one calendar)
        then starts a new thread that where the notification will be scheduled for 1 hour before the start time of event
        """
        current_date = datetime.datetime.now()
        one_hour = datetime.timedelta(hours=1)
        fifty_nine_minutes = datetime.timedelta(minutes=59)

        lower_bound = current_date + one_hour        
        upper_bound = lower_bound + fifty_nine_minutes

        lower_bound_time = lower_bound.time()
        upper_bound_time = upper_bound.time()

        events = DailyEvent.objects.filter(important=True)  # important events

        #if time is not 23:00
        #then get all events with start time between lower and upper bound on the same day
        if current_date.hour != 23:
            events = events.filter(
                schedule__name=str(datetime.date.today().isoweekday())
            )  # events that occur today

        #edge case when the time is 23pm as lower bound is then 00:00 on the next day
        #if time is 23
        #get all events that occur on next day from 
        else:  # events that occur the next day
            events = events.filter(
                schedule__name=str(datetime.date.today().isoweekday() + 1)
            )


        # events within lower and upper bound
        events = events.filter(
            start_time__gte=lower_bound_time
        )  

        events = events.filter(start_time__lte=upper_bound_time)

        # events that belong to a calendar that is last viewed
        events = events.filter(
            schedule__calendar__owner__last_viewed_cal=F("schedule__calendar")
        )  

        print(events)

        for event in events:
            # set up notification for each event
            new_thread = threading.Thread(target=notify, daemon=True, args=[event])
            new_thread.start()
            
    actual_job()
