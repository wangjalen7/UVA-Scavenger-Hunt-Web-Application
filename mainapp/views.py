from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EventForm, JoinEventForm, ThemeForm, TaskForm
from .models import Event, Player
from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm
from django.shortcuts import render
from django.shortcuts import redirect
# from django.views.generic import ListView
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
import requests
import googlemaps
from django.conf import settings # need api key from google to make the request


# from .models import HuntTemplate
# from .forms import HuntTemplateForm


def staff_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied
        return function(request, *args, **kwargs)

    return _inner

@login_required
def index(request):
    return render(request, 'index.html', {'user': request.user})

# Title: Django Google Maps Tutorial #4: Placing Markers on a Map
# URL: https://www.youtube.com/watch?v=sasx2ppol5c&t=685s 
def map_view(request):
    key = settings.GOOGLE_API_KEY

    return render(request, 'map.html', {'key': key})

# leave for now
def create_task(request):
    
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('/')

            # address = form.cleaned_data['location']
            # api_key = 'AIzaSyCamLJi3Ws33i65zxvez9nO9c1AqiFlElk'  # Replace with your actual API key

            # # Make a request to the Google Geocoding API
            # url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
            # response = requests.get(url)
            # data = response.json()

            # if data['status'] == 'OK':
            #     # Get the latitude and longitude from the API response
            #     location = data['results'][0]['geometry']['location']
            #     latitude = location['lat']
            #     longitude = location['lng']
            #     task = form.save(commit=False)
            #     task.save()
            #     return render(request, 'create_task.html', {
            #         'address': address,
            #         'latitude': latitude,
            #         'longitude': longitude,
            #         'google_maps_api_key': api_key,
            #     })
            # else:
            #     pass
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})

class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'


def join_event(request, event_id):
    event = Event.objects.get(id=event_id)
    player_user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        form = JoinEventForm(request.POST)
        if form.is_valid():
            try:
                queryset = Player.objects.get(event=event, user=player_user)
            except Player.DoesNotExist:
                queryset = None
            if queryset == None:
                player = form.save(commit=False)
                player.event = event
                player.user = player_user
                player.points = 0
                player.save()
                return redirect('/')
            else:
                return render(request, 'already_joined.html', context={'message': 'Already Joined'})
    else:
        form = JoinEventForm()
    return render(request, 'join_event.html', {'form': form, 'event': event.name, 'user': player_user.username})


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


@staff_only
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


@staff_only
@login_required
def approve_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.status = "approved"
    event.save()
    return redirect('manage_events')


@staff_only
@login_required
def deny_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.status = "denied"
    event.save()
    return redirect('manage_events')

@login_required
def leaderboard(request,):
    leaders = User.objects.alias(
        total_points=Sum('player__points')
    ).order_by('-total_points')[:10]
    return render(request, 'leaderboard.html', {'leaders': leaders})

@staff_only
@login_required
def create_theme(request):
    if request.method == "POST":
        form = ThemeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ThemeForm()
    return render(request, 'create_theme.html', {'form': form})

