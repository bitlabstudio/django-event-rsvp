"""Tests for the views of the ``event_rsvp`` app."""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from event_rsvp.models import Event
from event_rsvp.tests.factories import EventFactory, UserFactory, StaffFactory


class EventDetailViewTestCase(TestCase):
    """Tests for the ``EventDetailView`` view."""
    longMessage = True

    def test_view(self):
        self.event = EventFactory()
        resp = self.client.get(self.event.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

        # Test with wrong url kwargs
        resp = self.client.get(self.event.get_absolute_url().replace('2', '1'))
        self.assertEqual(resp.status_code, 404)


class EventCreateViewTestCase(TestCase):
    """Tests for the ``EventCreateView`` view."""
    longMessage = True

    def test_view(self):
        url = reverse('rsvp_event_create')

        # Login required
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

        # Staff rights required
        user = UserFactory()
        self.client.login(username=user.username, password='test123')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        staff = StaffFactory()
        self.client.login(username=staff.username, password='test123')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = {
            'title': 'Foo',
            'venue': 'Bar',
            'start': timezone.now(),
            'end': timezone.now() + timezone.timedelta(days=11),
            'max_seats_per_guest': 1,
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)


class EventUpdateViewTestCase(TestCase):
    """Tests for the ``EventUpdateView`` view."""
    longMessage = True

    def test_view(self):
        self.event = EventFactory()
        staff = StaffFactory()
        self.client.login(username=staff.username, password='test123')
        data = {
            'title': self.event.title,
            'venue': self.event.venue,
            'start': self.event.start,
            'end': self.event.end,
            'max_seats_per_guest': 20,
        }
        resp = self.client.post(self.event.get_update_url(), data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            Event.objects.get(pk=self.event.pk).max_seats_per_guest, 20)


class EventDeleteViewTestCase(TestCase):
    """Tests for the ``EventDeleteView`` view."""
    longMessage = True

    def test_view(self):
        self.event = EventFactory()
        staff = StaffFactory()
        self.client.login(username=staff.username, password='test123')
        resp = self.client.post(self.event.get_delete_url(),
                                data={'Foo': 'Bar'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Event.objects.all().count(), 0)


class EventCreateFromTemplateViewTestCase(TestCase):
    """Tests for the ``EventCreateFromTemplateView`` view."""
    longMessage = True

    def test_view(self):
        self.event = EventFactory()
        staff = StaffFactory()
        self.client.login(username=staff.username, password='test123')

        # Only callable if event is a template
        resp = self.client.get(self.event.get_template_url())
        self.assertEqual(resp.status_code, 404)

        self.event.template_name = 'Foo'
        self.event.save()
        resp = self.client.get(self.event.get_template_url())
        self.assertEqual(resp.status_code, 200)
        data = {
            'title': self.event.title,
            'venue': self.event.venue,
            'start': self.event.start,
            'end': self.event.end,
            'max_seats_per_guest': self.event.max_seats_per_guest,
        }
        resp = self.client.post(self.event.get_template_url(), data=data)
        self.assertEqual(resp.status_code, 302)

        # The template remains and a new event has been created
        self.assertEqual(Event.objects.all().count(), 2)


class StaffDashboardViewTestCase(TestCase):
    """Tests for the ``StaffDashboardView`` view."""
    longMessage = True

    def test_view(self):
        staff = StaffFactory()
        self.client.login(username=staff.username, password='test123')
        resp = self.client.get(reverse('rsvp_event_staff'))
        self.assertEqual(resp.status_code, 200)
