"""Django Admin-Settings for models of the ``event_rsvp`` application."""
from django.contrib import admin

from event_rsvp.models import Event, Guest


class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Event, EventAdmin)
admin.site.register(Guest)
