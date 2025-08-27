from .views import ScheduleCalendar, Schedule, DailyEvent

# helper functions 

def get_calendar(request, cal_id):
    """
    returns calendar with id cal_id if it belongs to the request's owner else None
    """
    try:
        calendar = ScheduleCalendar.objects.get(pk=cal_id)
    except ScheduleCalendar.DoesNotExist:
        return None

    if request.user == calendar.owner:
        return calendar


def get_schedule(request, sched_id):
    """
    returns schedule with id sched_id if it belongs to the request's owner else None
    """
    try:
        schedule = Schedule.objects.get(pk=sched_id)
    except Schedule.DoesNotExist:
        return None

    if request.user == schedule.calendar.owner:
        return schedule

    return None


def get_event(request, event_id):
    """
    returns event with id event_id if it belongs to the request's owner else None
    """
    try:
        event = DailyEvent.objects.get(pk=event_id)
    except DailyEvent.DoesNotExist:
        return None

    if request.user == event.schedule.calendar.owner:
        return event

    return None


