# flake8: noqa
from django_libs.loaders import load_member_from_setting
from event_rsvp import settings

from .base import EventForm

# importing GuestForm from settings
try:
    GuestForm = load_member_from_setting('GUEST_FORM', settings)
except:
    from .base import GuestForm
