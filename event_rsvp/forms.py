"""Forms for the ``event_rsvp`` app."""
from django import forms
from django.utils.translation import ugettext_lazy as _

from event_rsvp.models import Event, Guest


class EventForm(forms.ModelForm):
    """Form to handle specific validations of the Event model."""
    required_css_class = 'requiredField'

    def __init__(self, created_by, create_from_template=False, *args,
                 **kwargs):
        """
        :param created_by: Django-Auth User model, which is calling this view
        :param create_from_template: Boolean to know, if someone is using a
                                     template as draft.

        """
        self.instance = kwargs.get('instance')
        self.create_from_template = create_from_template
        if hasattr(self.instance, 'id') and not self.create_from_template:
            # Ignore the current user if it's the update view or if the
            # instance is a template
            self.created_by = self.instance.created_by
        else:
            # Add the current user as owner
            self.created_by = created_by
        if self.create_from_template:
            # If we use a template, the template_name is the only attribute,
            # which should not be preset
            self.instance.template_name = ''
        super(EventForm, self).__init__(*args, **kwargs)

        if self.instance.id and self.instance.template_name:
            self.this_is_a_template = True
        else:
            self.this_is_a_template = False

    def save(self, commit=True):
        """Saves twice if a template should be created."""
        if self.create_from_template:
            # Save a new event
            return forms.models.save_instance(
                self, Event(created_by=self.created_by), self._meta.fields,
                'created', commit, False)
        self.instance.created_by = self.created_by
        self.instance = super(EventForm, self).save(commit=True)
        if self.instance.template_name and not self.this_is_a_template:
            """
            If someone wants to save this instance as a template, create a
            second event as the template and keep the current instance in a
            'normal' condition. This is necessary, 'cause otherwise the
            template would keep the 'good' slug like 'foo-bar', while the new
            event got a slug like '_foo-bar'.

            """
            template = Event(template_name=self.instance.template_name,
                             created_by=self.created_by)
            self.instance.template_name = ''
            self.instance.save()
            forms.models.save_instance(
                self, template, self._meta.fields, 'created', commit, False)
        return self.instance

    class Meta:
        model = Event
        exclude = ('created_by', 'slug')


class GuestForm(forms.ModelForm):
    """Form to handle specific validations of the Guest model."""
    required_css_class = 'requiredField'

    def __init__(self, event, user, *args, **kwargs):
        """
        :param event: Event to participate
        :param user: Current user or anonymous.

        """
        self.event = event
        if user and user.is_authenticated():
            self.user = user
        else:
            self.user = None
        super(GuestForm, self).__init__(*args, **kwargs)
        if self.event.id:
            for field in self.event.required_fields:
                if field:
                    self.fields[field].required = True

    def clean_number_of_seats(self):
        data = self.cleaned_data['number_of_seats'] or 1
        free_seats = self.event.get_free_seats()
        if self.event.available_seats and free_seats < data:
            if free_seats == 1:
                msg = _('Sorry. There is only 1 seat left.')
            else:
                msg = _('Sorry. There are only %(amount)s seats left.') % {
                    'amount': free_seats}
            raise forms.ValidationError(msg)
        if (self.event.max_seats_per_guest > 0
                and data > self.event.max_seats_per_guest):
            if self.event.max_seats_per_guest == 1:
                msg = _('Pardon. There is only 1 seat per person reservable.')
            else:
                msg = _('Pardon. There are only %(amount)s seats per person'
                        ' reservable.') % {
                            'amount': self.event.max_seats_per_guest}
            raise forms.ValidationError(msg)
        return data

    def save(self, *args, **kwargs):
        self.instance.user = self.user
        self.instance.event = self.event
        super(GuestForm, self).save(*args, **kwargs)

    class Meta:
        model = Guest
        fields = ('name', 'email', 'phone', 'number_of_seats', 'message')
