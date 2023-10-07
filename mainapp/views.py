from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'index.html', {'user': request.user})




from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm

class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'




