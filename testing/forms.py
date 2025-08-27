from django.forms import ModelForm
from .models import DailyEvent, Schedule
from django import forms
from .models import ScheduleCalendar

class DailyEventForm(ModelForm):
    class Meta:
        model = DailyEvent
        fields = "__all__"


class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = ["calendar", "name"]

    def __init__(self,user, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        
        self.fields["calendar"] = forms.ModelChoiceField(queryset=ScheduleCalendar.objects.filter(owner=user))
    


    