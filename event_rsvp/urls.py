"""URLs for the ``event_rsvp`` app."""
from django.conf.urls.defaults import patterns, url

from event_rsvp.views import (
    EventCreateView,
    EventCreateFromTemplateView,
    EventDeleteView,
    EventDetailView,
    EventUpdateView,
    StaffDashboardView,
)


urlpatterns = patterns(
    '',
    url(
        r'^create/$',
        EventCreateView.as_view(),
        name='rsvp_event_create',
    ),

    url(
        r'^create-from-template/(?P<pk>\d+)/$',
        EventCreateFromTemplateView.as_view(),
        name='rsvp_event_create_from_template',
    ),

    url(
        r'^event-staff/$',
        StaffDashboardView.as_view(),
        name='rsvp_event_staff',
    ),

    url(
        r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/delete/$',  # nopep8
        EventDeleteView.as_view(),
        name='rsvp_event_delete',
    ),

    url(
        r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/update/$',  # nopep8
        EventUpdateView.as_view(),
        name='rsvp_event_update',
    ),

    url(
        r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        EventDetailView.as_view(),
        name='rsvp_event_detail',
    ),
)
