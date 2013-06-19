"""Models for the ``event_rsvp`` application."""
from django import forms
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import date, slugify
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from filer.fields.image import FilerImageField


class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        return value


class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices': self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(
                self.choices): ",".join([choicedict.get(
                    value, value) for value in getattr(self, fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)

    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if opt_select not in arr_choices:
                raise exceptions.ValidationError(
                    self.error_messages['invalid_choice'] % value)
        return

    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^event_rsvp\.models\.MultiSelectField"])


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
    :hide_available_seats: Checkfield to hide the information about available
      seats in the templates.
    :max_seats_per_guest: Maximum amount of seats per guest.
    :allow_anonymous_rsvp: Checkbox to allow anonymous responses.
    :required_fields: Checkbox to select required guest fields.
    :template_name: Name can be set, if this event should be reusable.
    :is_published: Checkbox to publish/unpublish an event.

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
        max_length=256,
        verbose_name=_('Title'),
        help_text=_('The title will also be used for the event URL.'),
    )

    slug = models.SlugField(
        max_length=256,
        verbose_name=_('Slug'),
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
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        verbose_name=_('City'),
        blank=True,
    )

    zip = models.CharField(
        max_length=100,
        verbose_name=_('ZIP code'),
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        verbose_name=_('Country'),
        blank=True,
    )

    contact_person = models.CharField(
        max_length=100,
        verbose_name=_('Contact name'),
        blank=True,
    )

    contact_email = models.EmailField(
        verbose_name=_('Contact email'),
        blank=True,
    )

    contact_phone = models.CharField(
        max_length=100,
        verbose_name=_('Contact phone'),
        blank=True,
    )

    available_seats = models.PositiveIntegerField(
        verbose_name=_('Available seats'),
        blank=True, null=True,
    )

    hide_available_seats = models.BooleanField(
        default=False,
        verbose_name=_('Hide available seat information'),
    )

    allow_anonymous_rsvp = models.BooleanField(
        default=False,
        verbose_name=_('Allow anonymous RSVP'),
        help_text=_('Even anonymous users can rsvp, without adding any info.'),
    )

    required_fields = MultiSelectField(
        verbose_name=_('Required fields'),
        max_length=250, blank=True,
        choices=(
            ('name', _('Name')),
            ('email', _('Email')),
            ('phone', _('Phone')),
        ),
    )

    max_seats_per_guest = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_('Maximum amount of seats per guest'),
    )

    template_name = models.CharField(
        max_length=100,
        verbose_name=_('Save as template'),
        blank=True,
        help_text=_('Save this event as a template to re-use it later.'),
    )

    is_published = models.BooleanField(
        verbose_name=_('is published'),
        default=False,
    )

    image = FilerImageField(
        verbose_name=_('Image'),
        related_name='rsvp_event_images',
        null=True, blank=True,
    )

    def __unicode__(self):
        if self.template_name:
            return '{0} ({1})'.format(self.template_name, ugettext('Template'))
        return '{0} ({1})'.format(self.title, date(self.start))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        suspects = Event.objects.filter(slug=self.slug)
        if suspects.count() > 0 and suspects[0] != self:
            while Event.objects.filter(slug=self.slug).count() > 0:
                try:
                    number = int(self.slug[-1])
                except ValueError:
                    self.slug = self.slug + '0'
                else:
                    self.slug = self.slug[:-1] + str(number + 1)
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self, url='rsvp_event_detail'):
        return reverse(url, kwargs={
            'slug': self.slug,
            'year': '{0:04d}'.format(self.start.year),
            'month': '{0:02d}'.format(self.start.month),
            'day': '{0:02d}'.format(self.start.day),
        })

    def get_update_url(self):
        return self.get_absolute_url(url='rsvp_event_update')

    def get_delete_url(self):
        return self.get_absolute_url(url='rsvp_event_delete')

    def get_template_url(self):
        return reverse('rsvp_event_create_from_template', kwargs={
            'pk': self.pk})

    def get_free_seats(self):
        reserved = self.guests.all().aggregate(models.Sum('number_of_seats'))
        if self.available_seats:
            return self.available_seats - int(reserved.get(
                'number_of_seats__sum') or 0)
        return _('Unlimited seats available.')

    def is_bookable(self):
        if self.start < timezone.now():
            return False
        return True


class Guest(models.Model):
    """
    Model to create event templates for recurring events etc.

    :event: Event to visit.
    :user: User model of the guest.
    :name: Name of the guest.
    :email: Email of the guest.
    :phone: Phone number of the guest.
    :number_of_seats: Amount of seats to book.
    :creation_date: Date of the guest model creation.
    :is_attending: If the user is attending or not. Default: True
    :message: A response from a potential attendee.

    """
    event = models.ForeignKey(
        'event_rsvp.Event',
        verbose_name=_('Event'),
        related_name='guests',
    )

    user = models.ForeignKey(
        'auth.User',
        verbose_name=_('User'),
        blank=True, null=True,
    )

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name'),
        blank=True,
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
    )

    phone = models.CharField(
        max_length=50,
        verbose_name=_('Phone'),
        blank=True,
    )

    number_of_seats = models.PositiveIntegerField(
        verbose_name=_('Number of seats'),
        blank=True, null=True,
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation date'),
    )

    is_attending = models.BooleanField(
        verbose_name=_('Attending'),
        default=True,
    )

    message = models.TextField(
        verbose_name=_('Message'),
        max_length=4000,
        blank=True,
    )

    def __unicode__(self):
        if self.user:
            return '{0} - {1}'.format(
                self.user.get_full_name() or self.user.email, self.event)
        elif self.name or self.email:
            return '{0} - {1}'.format(self.name or self.email, self.event)
        return '{0} - {1}'.format(ugettext('anonymous'), self.event)
