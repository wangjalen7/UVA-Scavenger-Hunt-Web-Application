from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ScavengerHuntForm
from .models import ScavengerHunt

@login_required
def index(request):
    return render(request, 'index.html', {'user': request.user})




from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm

class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'

def create_scavenger_hunt(request):
    if request.method == "POST":
        form = ScavengerHuntForm(request.POST)
        if form.is_valid():
            hunt = form.save(commit=False)
            hunt.status = "Pending"
            hunt.save()
            return redirect('/')
    else:
        form = ScavengerHuntForm()
    return render(request, 'create_scavenger_hunt.html', {'form': form})


def view_scavenger_hunts(request):
    hunts = ScavengerHunt.objects.all()
    return render(request, 'view_hunts.html', {'hunts': hunts})