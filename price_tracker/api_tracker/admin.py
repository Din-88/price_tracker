from django.contrib import admin

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


class TrackerAdmin(admin.ModelAdmin):
    list_display = ('url', 'date_time', 'price')


class UserTrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'tracker', 'notify')


admin.site.register(NotifyType)
admin.site.register(NotifyCase)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(UserTracker, UserTrackerAdmin)
admin.site.register(TrackersUserSettings)

admin.site.register(Price)
