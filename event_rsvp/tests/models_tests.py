"""Tests for models of the ``event_rsvp``` application."""
from django.test import TestCase

from event_rsvp.tests.factories import EventFactory, GuestFactory


class EventTestCase(TestCase):
    """Tests for the ``Event`` model class."""
    def test_model(self):
        obj = EventFactory()
        self.assertTrue(obj.pk)


class GuestTestCase(TestCase):
    """Tests for the ``Guest`` model class."""
    def test_model(self):
        obj = GuestFactory()
        self.assertTrue(obj.pk)
