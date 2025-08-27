from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import is_good_event, new_save_with_overlap

# Create your models here.
class User(AbstractUser):
    last_viewed_cal = models.OneToOneField(
        "ScheduleCalendar", on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        """
        check if new or already existing user, if new create default calendar else dont
        """

        unsaved: bool = self.id is None

        if unsaved:
            super().save(*args, **kwargs)

            default_calendar = ScheduleCalendar.objects.create(
                name="Default Calendar", owner=self
            )

            self.last_viewed_cal = default_calendar
            self.save()

        else:
            super().save(*args, **kwargs)


class Tasks(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title


class MiscellanousCalendar(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="misc_cal", blank=True
    )
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.owner}'s {self.name} calendar"


class Schedule(models.Model):
    NAME_CHOICES_VALUES = {
        "0": "Master",
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursay",
        "5": "Friday",
        "6": "Saturday",
        "7": "Sunday",
    }

    VALUE_CHOICES_VALUES = {"1": "Main", "2": "Alt1", "3": "Alt2"}

    NAME_CHOICES = (
        ("0", "Master"),
        ("1", "Monday"),
        ("2", "Tuesday"),
        ("3", "Wednesday"),
        ("4", "Thursay"),
        ("5", "Friday"),
        ("6", "Saturday"),
        ("7", "Sunday"),
    )

    VALUE_CHOICES = ((1, "Main"), (2, "Alt1"), (3, "Alt2"))

    calendar = models.ForeignKey(
        "ScheduleCalendar",
        on_delete=models.CASCADE,
        blank=True,
    )
    name = models.CharField(max_length=255, choices=NAME_CHOICES, blank=True)
    value = models.IntegerField(choices=VALUE_CHOICES, default=1, blank=True)

    class Meta:
        ordering = ["name", "value"]
        unique_together = [["calendar", "name", "value"]]

    def __str__(self):
        return f"{self.calendar}'s {self.get_name_display()} schedule"

    @property
    def events_set(self):
        #just want this to be a property
        return self.events.all()


class ScheduleCalendar(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="schedule_cals", blank=True
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.owner}'s {self.name} calendar"

    @property
    def schedules_set(self):
        #return id, name, values of all schedules in calendar
        return self.schedule_set.values("id", "name", "value")

    def save(self, *args, **kwargs):
        unsaved = self.id is None

        if unsaved:  # populate newly created calendar
            super().save(*args, **kwargs)
            for i in range(8):
                schedule = Schedule.objects.create(calendar=self, name=str(i))

        else:
            super().save(*args, **kwargs)


class DailyEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, blank=True, related_name="events"
    )
    important = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["start_time"]

    def save(self, *args, **kwargs):
        unsaved: bool = self.id is None

        if unsaved:
            other_events = self.schedule.events_set
        else:
            other_events = self.schedule.events_set.exclude(id=self.id)

        #kwarg indicating if object should be saved without checking if its time conflicts with others 
        bypass: bool = kwargs.pop("bypass", None) 

        #if we dont want to bypass error checking and other checks
        if not bypass:
            overlap = kwargs.pop("overlap", None)
            #if an event that shouldnt overlap with others
            if not overlap:
                try:
                    allowed = is_good_event(self, other_events)
                except ValueError:
                    raise ValueError("Bad times")
                
                if allowed:
                    super().save(*args, **kwargs)
            #event overlaps shift other events to make space
            else:
                new_save_with_overlap(self, other_events)
        #bypass checking for conflicts and others          
        else:
            super().save(*args, **kwargs)


class MiscEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    calendar = models.ForeignKey(MiscellanousCalendar, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
