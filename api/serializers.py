from rest_framework import serializers
from testing.models import ScheduleCalendar, Schedule, User, DailyEvent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class CalendarSerializer(serializers.ModelSerializer):
    # adding schedules so i can get all schedules that belong to a calendar without making multiple calls
    schedules = serializers.SerializerMethodField()

    class Meta:
        model = ScheduleCalendar
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_schedules(self, obj):
        return obj.schedules_set


class ScheduleSerializer(serializers.ModelSerializer):
    # adding events so i can get all events that belong to a schedule without doing multiple calls
    events = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = "__all__"
        depth = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_events(self, obj):
        return EventSerializer(obj.events_set, many=True).data


class EventSerializer(serializers.ModelSerializer):
    # this is cue to allow created events to overlap with others
    overlap = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = DailyEvent
        fields = "__all__"
        depth = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #inital object / queryset (group of objects) is made available through self.instance
        if self.instance:
            # changing the representation of start and end times here for easy displaying on front end
            try:
                for object in self.instance:
                    object.start_time = object.start_time.strftime("%H:%M")
                    object.end_time = object.end_time.strftime("%H:%M")

            except:
                self.instance.start_time = self.instance.start_time.strftime("%H:%M")
                self.instance.end_time = self.instance.end_time.strftime("%H:%M")

    def create(self, validated_data):
        # differentiating between events that will overlap or not
        overlap = validated_data.pop("overlap", None)
        to_create = DailyEvent(**validated_data)

        if not overlap:
            to_create.save()
            
        else:
            to_create.save(overlap=True)

        return to_create
    
    def update(self, instance,validated_data):
        # differentiating between events that will overlap or not
        overlap = validated_data.pop("overlap", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if not overlap:
            instance.save()
        else:
            instance.save(overlap=True)

        return instance
