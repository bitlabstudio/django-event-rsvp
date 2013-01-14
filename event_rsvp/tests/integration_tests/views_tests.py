"""Tests for the views of the ``event_rsvp`` app."""
from django.test import TestCase
from django.utils import timezone

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewTestMixin

from event_rsvp.models import Event
from event_rsvp.tests.factories import EventFactory, StaffFactory


class EventDetailViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``EventDetailView`` view."""
    longMessage = True

    def test_view(self):
        self.event = EventFactory()
        self.should_be_callable_when_anonymous(self.event.get_absolute_url())

        # Test with wrong url kwargs
        resp = self.client.get(self.event.get_absolute_url().replace('2', '1'))
        self.assertEqual(resp.status_code, 404)


class EventCreateViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``EventCreateView`` view."""
    longMessage = True

    def setUp(self):
        self.user = UserFactory()
        self.staff = StaffFactory()

    def get_view_name(self):
        return 'rsvp_event_create'

    def test_view(self):
        # Staff rights required
        self.is_not_callable(user=self.user)

        self.should_be_callable_when_authenticated(self.staff)
        data = {
            'title': 'Foo',
            'venue': 'Bar',
            'start': timezone.now(),
            'end': timezone.now() + timezone.timedelta(days=11),
            'max_seats_per_guest': 1,
        }
        self.is_callable('POST', data=data)


class EventUpdateViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``EventUpdateView`` view."""
    longMessage = True

    def get_url(self, *args, **kwargs):
        return self.event.get_update_url()

    def setUp(self):
        self.event = EventFactory()
        self.staff = StaffFactory()

    def test_view(self):
        data = {
            'title': self.event.title,
            'venue': self.event.venue,
            'start': self.event.start,
            'end': self.event.end,
            'max_seats_per_guest': 20,
        }
        self.is_callable('POST', data=data, user=self.staff)
        self.assertEqual(
            Event.objects.get(pk=self.event.pk).max_seats_per_guest, 20)


class EventDeleteViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``EventDeleteView`` view."""
    longMessage = True

    def get_url(self, *args, **kwargs):
        return self.event.get_delete_url()

    def setUp(self):
        self.event = EventFactory()
        self.staff = StaffFactory()

    def test_view(self):
        self.is_callable('POST', data={'Foo': 'Bar'}, user=self.staff)
        self.assertEqual(Event.objects.all().count(), 0)


class EventCreateFromTemplateViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``EventCreateFromTemplateView`` view."""
    longMessage = True

    def get_url(self, *args, **kwargs):
        return self.event.get_template_url()

    def setUp(self):
        self.event = EventFactory()
        self.staff = StaffFactory()

    def test_view(self):
        # Only callable if event is a template
        self.is_not_callable(user=self.staff)

        self.event.template_name = 'Foo'
        self.event.save()
        self.is_callable(user=self.staff)
        data = {
            'title': self.event.title,
            'venue': self.event.venue,
            'start': self.event.start,
            'end': self.event.end,
            'max_seats_per_guest': self.event.max_seats_per_guest,
        }
        self.is_callable('POST', data=data, user=self.staff)

        # The template remains and a new event has been created
        self.assertEqual(Event.objects.all().count(), 2)


class StaffDashboardViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``StaffDashboardView`` view."""
    longMessage = True

    def get_view_name(self):
        return 'rsvp_event_staff'

    def test_view(self):
        staff = StaffFactory()
        self.is_callable(user=staff)
