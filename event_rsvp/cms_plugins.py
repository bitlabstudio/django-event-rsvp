"""CMS Plugins for the ``event_rsvp`` app."""
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Event


class CMSEventPlugin(CMSPluginBase):
    name = _('Upcoming Events')
    render_template = 'event_rsvp/upcoming_events.html'

    def render(self, context, instance, placeholder):
        context.update({
            'events': Event.objects.filter(start__gt=now(),
                                           is_published=True)[:3],
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSEventPlugin)
