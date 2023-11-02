from allauth.account.forms import SignupForm
from django import forms
from .models import Task, Theme, Team, Event, Player
from django.forms.widgets import DateInput
from django.forms import inlineformset_factory


class AllauthCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)

    def save(self, request):
        user = super(AllauthCustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class EventForm(forms.ModelForm):
    password = forms.CharField(
        label='Password (only for private events)',
        required=False
    )
    class Meta:
        model = Event
        fields = ['name', 'start_date', 'end_date', 'privacy', 'password', 'description', 'theme']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'privacy': forms.Select(choices=Event.PRIVACY_CHOICES),
        }


def clean(self):
    cleaned_data = super().clean()
    privacy = cleaned_data.get('privacy')
    join_password = cleaned_data.get('join_password')

    if privacy == 'private' and not join_password:
        self.add_error('join_password', 'Password is required for private events.')
    return cleaned_data


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'task', 'hint', 'latitude', 'longitude', 'theme']


TaskFormSet = inlineformset_factory(
    Theme, Task,
    fields=('name', 'task', 'hint', 'latitude', 'longitude'),
    extra=1,
    can_delete=True  # Ensure this is True
)


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['team']

        model = Theme
        fields = ['title', 'description']


class JoinTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['id']  # This field will be populated from the hidden input in the template.


class CreateTeamForm(forms.Form):
    new_team_name = forms.CharField(
        label='New Team Name',
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Enter new team name'})
    )


class JoinPrivateEventForm(forms.Form):
    password = forms.CharField(
        label='Event Password',
        max_length=255,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter event password'})
    )
