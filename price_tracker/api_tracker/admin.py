from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User


# from profile.models import User


from .models import (
    NotifyType,
    NotifyCase,
    Tracker,
    UserTracker,
    Price,
    TrackersUserSettings,
)


class PriceInline(admin.TabularInline):
    model = Price
    extra = 1
    max_num = 10


# class UsersInline(admin.TabularInline):
#     model = User # settings.AUTH_USER_MODEL


class TrackerAdmin(admin.ModelAdmin):
    # inlines = [PriceInline, UsersInline]
    list_display = ('url', 'date_time', 'price')
    # fields = ['pub_date', 'question_text']


class UserTrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'tracker', 'notify')
    # fields = ['pub_date', 'question_text']


admin.site.register(NotifyType)
admin.site.register(NotifyCase)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(UserTracker, UserTrackerAdmin)
admin.site.register(TrackersUserSettings)

admin.site.register(Price)
