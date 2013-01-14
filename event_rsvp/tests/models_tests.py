"""Tests for models of the ``event_rsvp``` application."""
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from event_rsvp.tests.factories import EventFactory, GuestFactory


class EventTestCase(TestCase):
    """Tests for the ``Event`` model class."""
    def test_model(self):
        obj = EventFactory()
        self.assertTrue(obj.pk)

    def test_get_free_seats(self):
        event_1 = EventFactory(available_seats=20)
        self.assertEqual(event_1.get_free_seats(), 20)
        event_2 = EventFactory()
        self.assertEqual(event_2.get_free_seats(),
                         _('Unlimited seats available.'))
        GuestFactory(event=event_1)
        self.assertEqual(event_1.get_free_seats(), 19)

    def test_is_bookable(self):
        event_1 = EventFactory()
        self.assertFalse(event_1.is_bookable())
        event_2 = EventFactory(
            start=timezone.now() + timezone.timedelta(days=5),
            end=timezone.now() + timezone.timedelta(days=15),
        )
        self.assertTrue(event_2.is_bookable())


class GuestTestCase(TestCase):
    """Tests for the ``Guest`` model class."""
    def test_model(self):
        obj = GuestFactory()
        self.assertTrue(obj.pk)
