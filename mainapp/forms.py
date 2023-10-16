from allauth.account.forms import SignupForm
from django import forms
from .models import ScavengerHunt, Player

class AllauthCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)

    def save(self, request):
        user = super(AllauthCustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

class ScavengerHuntForm(forms.ModelForm):
    class Meta:
        model = ScavengerHunt
        fields = ['name', 'start_date', 'end_date', 'creator', 'privacy', 'description']

class JoinHuntForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['hunt', 'user', 'team']