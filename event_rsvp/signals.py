"""Signals for the event_rsvp app."""
from django import dispatch

post_guest_create = dispatch.Signal(providing_args=['user', 'event'])
