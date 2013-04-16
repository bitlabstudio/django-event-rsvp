"""Views for the ``event_rsvp`` app."""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.utils.decorators import method_decorator

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from event_rsvp.forms import EventForm, GuestForm
from event_rsvp.models import Event, Guest


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
            redirect_url = getattr(self.object, 'get_{0}_url'.format(
                self.url_mode))
            return HttpResponseRedirect(redirect_url())
        return super(EventSecurityMixin, self).dispatch(request, *args,
                                                        **kwargs)


class GuestViewMixin(object):
    """Mixin to handle guest-specific functions."""
    model = Guest
    form_class = GuestForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(slug=kwargs.get('event_slug'))
        except Event.DoesNotExist:
            raise Http404
        return super(GuestViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GuestViewMixin, self).get_context_data(**kwargs)
        context.update({'event': self.event, 'user': self.request.user})
        if (self.request.user.is_authenticated()
                or self.event.allow_anonymous_rsvp):
            context.update({'permission_to_book': True})
        return context

    def get_form_kwargs(self):
        kwargs = super(GuestViewMixin, self).get_form_kwargs()
        kwargs.update({'event': self.event, 'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return self.event.get_absolute_url()


class GuestSecurityMixin(object):
    """Mixin to handle guest-specific security options."""
    def get_object(self, *args, **kwargs):
        obj = super(GuestSecurityMixin, self).get_object(*args, **kwargs)
        if obj.event != self.event:
            raise Http404
        return obj


#--------#
# Views  #
#--------#

class EventListView(ListView):
    """List view to display upcoming events."""
    def get_queryset(self):
        return Event.objects.filter(start__gt=timezone.now(),
                                    is_published=True)

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context.update({
                'my_participations': self.request.user.guest_set.all()})
        return context


class EventDetailView(EventSecurityMixin, EventViewMixin, DetailView):
    """Detail view to display information of an event."""
    url_mode = 'absolute'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.object = self.get_object()
        if not self.object.is_published and not request.user.is_staff:
            raise Http404
        return super(EventDetailView, self).dispatch(request, *args, **kwargs)


class EventCreateView(StaffMixin, EventViewMixin, CreateView):
    """Create view to handle information of an event."""
    pass


class EventUpdateView(StaffMixin, EventSecurityMixin, EventViewMixin,
                      UpdateView):
    """Update view to handle information of an event."""
    url_mode = 'update'


class EventDeleteView(StaffMixin, EventSecurityMixin, EventViewMixin,
                      DeleteView):
    """Delete view to remove the relevant event."""
    url_mode = 'delete'


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


class GuestDetailView(StaffMixin, GuestSecurityMixin, GuestViewMixin,
                      DetailView):
    """View to display guest related functions and lists."""
    pass


class GuestCreateView(GuestViewMixin, CreateView):
    """Create view to add a guest to an event."""
    def get_form_kwargs(self):
        kwargs = super(GuestCreateView, self).get_form_kwargs()
        if self.request.user.is_authenticated():
            kwargs.update({'initial': {
                'name': self.request.user.get_full_name(),
                'email': self.request.user.email}})
        return kwargs


class GuestUpdateView(GuestSecurityMixin, GuestViewMixin, UpdateView):
    """Update view to handle a guest."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(slug=kwargs.get('event_slug'))
        except Event.DoesNotExist:
            raise Http404
        self.kwargs = kwargs
        self.object = self.get_object()
        if (not request.user.is_staff and not self.object.user
                and not self.object.user == request.user):
            raise Http404
        return super(GuestViewMixin, self).dispatch(request, *args, **kwargs)


class GuestDeleteView(StaffMixin, GuestViewMixin, GuestSecurityMixin,
                      DeleteView):
    """Delete view to remove the relevant guest."""
    pass
