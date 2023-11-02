from allauth.account.forms import SignupForm
from django import forms
from .models import Event, Player

class AllauthCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)

    def save(self, request):
        user = super(AllauthCustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

from django.forms.widgets import DateInput

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'start_date', 'end_date', 'privacy', 'description', 'privacy']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'privacy': forms.Select(choices=Event.PRIVACY_CHOICES),
        }



class JoinEventForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['team']

