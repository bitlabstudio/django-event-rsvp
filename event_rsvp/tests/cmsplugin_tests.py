"""Tests for models of the ``event_rsvp``` application."""
from django.test import TestCase
from django.utils import timezone

from ..cms_plugins import CMSEventPlugin
from .factories import EventFactory


class CMSEventPluginTestCase(TestCase):
    """Tests for the ``CMSEventPlugin`` cmsplugin."""
    longMessage = True

    def setUp(self):
        self.event = EventFactory(start=timezone.now() + timezone.timedelta(
            days=1), is_published=True)
        self.cmsplugin = CMSEventPlugin()

    def test_render(self):
        self.assertEqual(
            self.cmsplugin.render({}, None, None).get('events')[0], self.event)
