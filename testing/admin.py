from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Tasks)
admin.site.register(ScheduleCalendar)
admin.site.register(MiscellanousCalendar)
admin.site.register(Schedule)
admin.site.register(DailyEvent)
admin.site.register(MiscEvent)


