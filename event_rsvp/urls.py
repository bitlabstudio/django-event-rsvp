"""URLs for the ``event_rsvp`` app."""
from django.conf.urls.defaults import patterns, url

from event_rsvp.views import (
    EventCreateView,
    EventCreateFromTemplateView,
    EventDeleteView,
    EventDetailView,
    EventListView,
    EventUpdateView,
    GuestCreateView,
    GuestDeleteView,
    GuestDetailView,
    GuestUpdateView,
    StaffDashboardView,
)


urlpatterns = patterns(
    '',
    url(
        r'^$',
        EventListView.as_view(),
        name='rsvp_event_list',
    ),

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

    url(
        r'^guest/(?P<event_slug>[-\w]+)/create/$',
        GuestCreateView.as_view(),
        name='rsvp_guest_create',
    ),

    url(
        r'^guest/(?P<event_slug>[-\w]+)/(?P<pk>\d+)/update/$',
        GuestUpdateView.as_view(),
        name='rsvp_guest_update',
    ),

    url(
        r'^guest/(?P<event_slug>[-\w]+)/(?P<pk>\d+)/delete/$',
        GuestDeleteView.as_view(),
        name='rsvp_guest_delete',
    ),

    url(
        r'^guest/(?P<event_slug>[-\w]+)/(?P<pk>\d+)/$',
        GuestDetailView.as_view(),
        name='rsvp_guest_detail',
    ),
)
