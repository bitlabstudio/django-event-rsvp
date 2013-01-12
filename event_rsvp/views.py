"""Views for the ``event_rsvp`` app."""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from event_rsvp.forms import EventForm
from event_rsvp.models import Event


#--------#
# Mixins #
#--------#

class StaffMixin(object):
    """Mixin to let only staff member pass."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return super(StaffMixin, self).dispatch(request, *args, **kwargs)


class EventViewMixin(object):
    """Mixin to handle event-specific options."""
    model = Event
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super(EventViewMixin, self).get_form_kwargs()
        kwargs.update({'created_by': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('rsvp_event_staff')


class EventSecurityMixin(object):
    """Mixin to handle event-specific security options."""

    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.object = self.get_object()
        date = self.object.start
        # Check the right starting date within the slug
        if (date.year != int(kwargs.get('year'))
                or date.month != int(kwargs.get('month'))
                or date.day != int(kwargs.get('day'))):
            raise Http404
        return super(EventSecurityMixin, self).dispatch(request, *args,
                                                        **kwargs)


#--------#
# Views  #
#--------#

class EventDetailView(EventSecurityMixin, EventViewMixin, DetailView):
    """Detail view to display information of an event."""
    pass


class EventCreateView(StaffMixin, EventViewMixin, CreateView):
    """Create view to handle information of an event."""
    pass


class EventUpdateView(StaffMixin, EventSecurityMixin, EventViewMixin,
                      UpdateView):
    """Update view to handle information of an event."""
    pass


class EventDeleteView(StaffMixin, EventSecurityMixin, EventViewMixin,
                      DeleteView):
    """Update view to handle information of an event."""
    pass


class EventCreateFromTemplateView(StaffMixin, EventViewMixin, CreateView):
    """Create view to create information of an event from a template."""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            # Check if it's really a template
            self.template = Event.objects.get(pk=kwargs.get('pk'),
                                              template_name__gt='')
        except Event.DoesNotExist:
            raise Http404
        return super(EventCreateFromTemplateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(EventCreateFromTemplateView, self).get_form_kwargs()
        kwargs.update({'instance': self.template,
                       'create_from_template': True})
        return kwargs


class StaffDashboardView(StaffMixin, ListView):
    """View to display event related functions and lists."""
    model = Event
    template_name = 'event_rsvp/staff_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(StaffDashboardView, self).get_context_data(**kwargs)
        templates = self.object_list.exclude(template_name__exact='')
        self.object_list = self.object_list.filter(template_name__exact='')
        context.update({
            'upcoming': self.object_list.filter(start__gt=timezone.now()),
            'current': self.object_list.filter(start__lte=timezone.now(),
                                               end__gte=timezone.now()),
            'past': self.object_list.filter(end__lt=timezone.now()),
            'templates': templates,
        })
        return context
