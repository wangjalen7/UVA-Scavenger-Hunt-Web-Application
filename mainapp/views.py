from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ScavengerHuntForm
from .models import ScavengerHunt
from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView

@login_required
def index(request):
    return render(request, 'index.html', {'user': request.user})


class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'

class ListScavengerHunt(ListView):
    model = ScavengerHunt
    template_name = "public_events.html"
    context_object_name="scavenger_hunt_list"

    def get_queryset(self):
        return ScavengerHunt.objects.filter(privacy = "public")


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

def manage_scavenger_hunts(request):
    hunts = ScavengerHunt.objects.all()
    return render(request, 'manage_scavenger_hunts.html', {'hunts': hunts})


def approve_hunt(request, hunt_id):
    hunt = ScavengerHunt.objects.get(id=hunt_id)
    hunt.status = "approved"
    hunt.save()
    return redirect('manage_scavenger_hunts')

def deny_hunt(request, hunt_id):
    hunt = ScavengerHunt.objects.get(id=hunt_id)
    hunt.status = "denied"
    hunt.save()
    return redirect('manage_scavenger_hunts')
