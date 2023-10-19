from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EventForm, JoinHuntForm
from .models import Event, Player
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

class ListEvents(ListView):
    model = Event
    template_name = "public_events.html"
    context_object_name="events_list"

    def get_queryset(self):
        return Event.objects.filter(privacy = "U")
    
def join_hunt(request, event_id):
    scav_hunt = Event.objects.get(id=event_id)
    player_user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        form = JoinHuntForm(request.POST)
        if form.is_valid():
            # try:
            #     queryset = Player.objects.get(hunt=scav_hunt, user=player_user)
            # except Player.DoesNotExist:
            #     queryset = None
            # if queryset != None:
            #     return render(request,'already_joined.html', context={'message': 'Already Joined'})
            # else:
                player = form.save(commit=False)
                player.hunt = scav_hunt
                player.user = player_user
                player.points = 0
                player.save()
                return redirect('/')
    else:
        form = JoinHuntForm()
    return render(request, 'join_scavenger_hunt.html', {'form': form, 'hunt': scav_hunt.name, 'user': player_user.username})

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user  # Set the creator as the current user
            event.status = "pending"
            event.save()
            return redirect('/')
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})

@login_required
def view_public_events(request):
    events = Event.objects.filter(status='approved', privacy='U')
    return render(request, 'view_events.html', {'events': events, 'title': "Public Events"})

@login_required
def view_my_events(request):
    events = Event.objects.filter(creator=request.user)
    return render(request, 'view_events.html', {'events': events, 'title': "My Events"})

@login_required
def manage_events(request):
    events_pending = Event.objects.filter(status='pending', privacy='U')
    events_approved = Event.objects.filter(status='approved', privacy='U')
    events_denied = Event.objects.filter(status='denied', privacy='U')

    context = {
        'events_pending': events_pending,
        'events_approved': events_approved,
        'events_denied': events_denied,
    }

    return render(request, 'manage_events.html', context)

@login_required
def approve_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.status = "approved"
    event.save()
    return redirect('manage_events')

@login_required
def deny_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.status = "denied"
    event.save()
    return redirect('manage_events')
