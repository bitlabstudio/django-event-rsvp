"""Factories to test models of the ``event_rsvp``` application."""
from django_libs.tests.factories import UserFactory
import factory

from event_rsvp.models import Event, Guest


class StaffFactory(UserFactory):
    is_staff = True


class EventFactory(factory.Factory):
    FACTORY_FOR = Event

    created_by = factory.SubFactory(UserFactory)
    title = 'Foo'
    venue = 'Bar'


class GuestFactory(factory.Factory):
    FACTORY_FOR = Guest

    event = factory.SubFactory(EventFactory)
    number_of_seats = 1
