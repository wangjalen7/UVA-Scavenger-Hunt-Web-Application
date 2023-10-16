from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ScavengerHuntForm, JoinHuntForm
from .models import ScavengerHunt, Player
from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.models import User

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
    
def join_hunt(request, hunt_id):
    scav_hunt = ScavengerHunt.objects.get(id=hunt_id)
    player_user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        form = JoinHuntForm(request.POST)
        if form.is_valid():
            try:
                queryset = Player.objects.get(hunt=scav_hunt, user=player_user)
            except Player.DoesNotExist:
                queryset = None
            if queryset == None:
                player = form.save(commit=False)
                player.hunt = scav_hunt
                player.user = player_user
                player.points = 0
                player.save()
                return redirect('/')
            else:
                return render(request,'already_joined.html', context={'message': 'Already Joined'})
    else:
        form = JoinHuntForm()
    return render(request, 'join_scavenger_hunt.html', {'form': form, 'hunt': scav_hunt.name, 'user': player_user.username})

def create_scavenger_hunt(request):
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        form = ScavengerHuntForm(request.POST)
        if form.is_valid():
            hunt = form.save(commit=False)
            hunt.status = "Pending"
            hunt.creator=user
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
