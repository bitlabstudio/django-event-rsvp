"""Tests for the forms of the ``event_rsvp`` app."""
from django.test import TestCase
from django.utils import timezone

from django_libs.tests.factories import UserFactory

from event_rsvp.forms import EventForm, GuestForm
from event_rsvp.models import Event, Guest
from event_rsvp.tests.factories import EventFactory


class EventFormTestCase(TestCase):
    """Tests for the ``EventForm`` form class."""
    longMessage = True

    def test_validates_and_saves_input(self):
        self.user = UserFactory()
        data = {
            'title': 'Foo',
            'venue': 'Bar',
            'start': timezone.now(),
            'end': timezone.now() + timezone.timedelta(days=11),
            'max_seats_per_guest': 1,
        }
        form = EventForm(data=data, created_by=self.user)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(Event.objects.all().count(), 1)

        # Test update
        data.update({'street': 'Foostreet'})
        form = EventForm(data=data, instance=instance, created_by=self.user)
        instance = form.save()
        self.assertEqual(instance.street, 'Foostreet')

        # Test creating an event from a template
        form = EventForm(data=data, instance=instance, created_by=self.user,
                         create_from_template=True)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(Event.objects.all().count(), 2)

        # Test saving a template
        data.update({'template_name': 'Foo'})
        form = EventForm(data=data, created_by=self.user)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(
            Event.objects.exclude(template_name__exact='').count(), 1)

        # Test updating a template
        data.update({'street': 'Barstreet'})
        form = EventForm(data=data, instance=instance, created_by=self.user)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.street, 'Barstreet')


class GuestFormTestCase(TestCase):
    """Tests for the ``GuestForm`` form class."""
    longMessage = True

    def test_validates_and_saves_input(self):
        self.event = EventFactory(available_seats=20)
        form = GuestForm(data={'number_of_seats': 100}, event=self.event,
                         user=None)
        self.assertFalse(form.is_valid())
        form = GuestForm(data={}, event=self.event, user=None)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Guest.objects.all().count(), 1)
