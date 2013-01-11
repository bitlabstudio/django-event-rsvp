"""Models for the ``event_rsvp`` application."""
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    """
    Model to create event templates for recurring events etc.

    :created_by: User, who owns this template.
    :creation_date: Date of the template creation.
    :title: Title of the template.
    :description: Description of the template.
    :start: Starting date of the event.
    :end: Ending date of the event.
    :venue: The event location.
    :street: Street of the event location.
    :city: City of the event location.
    :zip: ZIP code of the event location.
    :country: Country of the event location.
    :contact_person: Name of a person to contact.
    :contact_email: Email of a person to contact.
    :contact_phone: Phone of a person to contact.
    :available_seats: Amount of seats available for this event.
    :max_seats_per_guest: Maximum amount of seats per guest.
    :allow_anonymous_rsvp: Checkbox to allow anonymous responses.
    :require_name_and_email: Checkbox to require a name and an email within the
                             response.
    :template_name: Name can be set, if this event should be reusable.

    """
    created_by = models.ForeignKey(
        'auth.User',
        verbose_name=_('Created by'),
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation date'),
    )

    title = models.CharField(
        max_length=50,
        verbose_name=_('Title'),
    )

    description = models.TextField(
        max_length=1000,
        verbose_name=_('Description'),
        blank=True, null=True,
    )

    start = models.DateTimeField(
        default=timezone.now(),
        verbose_name=_('Start date'),
    )

    end = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=1),
        verbose_name=_('End date'),
    )

    venue = models.CharField(
        max_length=100,
        verbose_name=_('Venue'),
    )

    street = models.CharField(
        max_length=100,
        verbose_name=_('Street'),
        blank=True, null=True,
    )

    city = models.CharField(
        max_length=100,
        verbose_name=_('City'),
        blank=True, null=True,
    )

    zip = models.CharField(
        max_length=100,
        verbose_name=_('ZIP code'),
        blank=True, null=True,
    )

    country = models.CharField(
        max_length=100,
        verbose_name=_('Country'),
        blank=True, null=True,
    )

    contact_person = models.CharField(
        max_length=100,
        verbose_name=_('Contact name'),
        blank=True, null=True,
    )

    contact_email = models.EmailField(
        verbose_name=_('Contact email'),
        blank=True, null=True,
    )

    contact_phone = models.CharField(
        max_length=100,
        verbose_name=_('Contact phone'),
        blank=True, null=True,
    )

    available_seats = models.PositiveIntegerField(
        verbose_name=_('Available seats'),
        blank=True, null=True,
    )

    allow_anonymous_rsvp = models.BooleanField(
        default=False,
        verbose_name=_('Allow anonymous RSVP'),
    )

    require_name_and_email = models.BooleanField(
        default=False,
        verbose_name=_('Require name & email'),
    )

    max_seats_per_guest = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Maximum amount of seats per guest'),
    )

    template_name = models.CharField(
        max_length=100,
        verbose_name=_('Save as template'),
        blank=True, null=True,
    )

    def __unicode__(self):
        if self.template_name:
            return '{0} ({1})'.format(self.template_name, _('Template'))
        return '{0} ({1})'.format(self.title, self.start)


class Guest(models.Model):
    """
    Model to create event templates for recurring events etc.

    :event: Event to visit.
    :user: User model of the guest.
    :name: Name of the guest.
    :email: Email of the guest.
    :number_of_seats: Amount of seats to book.
    :creation_date: Date of the guest model creation.

    """
    event = models.ForeignKey(
        'event_rsvp.Event',
        verbose_name=_('User'),
    )

    user = models.ForeignKey(
        'auth.User',
        verbose_name=_('User'),
        blank=True, null=True,
    )

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name'),
        blank=True, null=True,
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True, null=True,
    )

    number_of_seats = models.PositiveIntegerField(
        verbose_name=_('Number of seats'),
        blank=True, null=True,
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation date'),
    )

    def __unicode__(self):
        if self.user:
            return '{0} ({1})'.format(self.user.get_full_name(), self.event)
        elif self.name or self.email:
            return '{0} ({1})'.format(self.name or self.email, self.event)
        return '{0} ({1})'.format(_('anonymous'), self.event)