from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EventForm, TaskForm, ThemeForm, JoinTeamForm, CreateTeamForm, TaskFormSet
from .models import Event, Theme, Task, Team, UserProfile, Achievements, Player, UserProfile
from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
import logging
from django.contrib import messages
import requests
import googlemaps
from django.conf import settings # need api key from google to make the request


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ScavengerHuntApp')


def staff_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied
        return function(request, *args, **kwargs)

    return _inner


# Title: Django Google Maps Tutorial #4: Placing Markers on a Map
# URL: https://www.youtube.com/watch?v=sasx2ppol5c&t=685s 
def map_view(request):
    key = settings.GOOGLE_API_KEY

    return render(request, 'map.html', {'key': key})



class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'


@login_required
def profile(request):
    user = request.user
    achievements = Achievements.objects.filter(user=user)
    user_points = Player.objects.filter(user=user).aggregate(total_points=Sum('points'))['total_points'] or 0

    return render(request, 'profile/profile.html', {
        'user': user,
        'achievements': achievements,
        'user_points': user_points,
    })
@login_required
def change_username(request):
    username_error = ""
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        user = request.user
        if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            username_error = 'This username is already in use. Please choose a different one.'
        else:
            user.username = new_username
            user.save()
            return redirect('profile')
    return render(request, 'profile/change_username.html', {'user': request.user, 'username_error': username_error})
@login_required
def change_bio(request):
        bio_error = ""
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        if request.method == 'POST':
            new_bio = request.POST.get('bio')
            if len(new_bio) > 250:
                bio_error = 'Bio must be 250 characters or less.'
            else:
                user_profile.bio = new_bio
                user_profile.save()
                return redirect('profile')
        else:
            new_bio = user_profile.bio
        return render(request, 'profile/change_bio.html', {'user': request.user, 'bio_error': bio_error, 'bio': new_bio})
@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
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
def event_details(request, event_id, tab='about'):
    event = Event.objects.get(pk=event_id)
    is_member = Team.objects.filter(event=event, members=request.user).exists()
    teams = Team.objects.filter(event=event)

    theme = event.theme

    tasks = Task.objects.filter(theme=theme)

    context = {
        'event': event,
        'is_member': is_member,
        'tab': tab,
        'teams': teams,
        'tasks': tasks,
        'theme': theme,
    }
    return render(request, 'event_details.html', context)


@login_required
def team_details(request, event_id, team_id):
    event = get_object_or_404(Event, pk=event_id)
    team = get_object_or_404(Team, pk=team_id, event=event)
    members = team.members.all()
    return render(request, 'event_details.html', {'event': event, 'team': team, 'members': members, 'tab': 'team'})



@login_required
def join_team(request, event_id, team_id):
    event = get_object_or_404(Event, pk=event_id)
    team_to_join = get_object_or_404(Team, pk=team_id, event=event)

    if team_to_join.members.filter(id=request.user.id).exists():
        return render(request, 'error.html', context = {'message': 'You have already joined this team'})

    current_team = Team.objects.filter(event=event, members=request.user).first()
    if current_team:
        current_team.members.remove(request.user)
        team_to_join.members.add(request.user)
        messages.success(request, "You have switched to a new team.")
    else:
        team_to_join.members.add(request.user)
        messages.success(request, "You have successfully joined the team.")

    return redirect('event_details', event_id=event_id, tab='about')

@login_required
def create_team(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            new_team_name = form.cleaned_data['new_team_name']
            new_team = Team.objects.create(name=new_team_name, event=event)
            new_team.members.add(request.user)
            messages.success(request, "Team created successfully.")
            return redirect('event_details', event_id=event_id, tab='about')
    

    if Team.objects.filter(members=request.user, event=event).exists():
        return render(request, 'error.html', context = {'message': 'You have already joined a team'})

    create_team_form = CreateTeamForm()
    context = {
        'event': event,
        'create_team_form': create_team_form,
    }
    return render(request, 'create_team.html', context)


@login_required
def error(request):
     return render(request, 'error.html', context = {'message': 'You have already joined this team'})

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


import json

@staff_only
@login_required
def create_theme(request):
    if request.method == 'POST':
        form = ThemeForm(request.POST)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.creator = request.user
            theme.save()
            
            task_data = json.loads(request.POST.get('tasks_json', '[]'))

            for task_info in task_data:
                Task.objects.create(
                    name=task_info.get('name', ''),
                    task=task_info.get('task', ''),
                    hint=task_info.get('hint', ''),
                    latitude=task_info.get('latitude', ''),
                    longitude=task_info.get('longitude', ''),
                    theme=theme
                )
            
            return redirect('home')

    else:
        theme_form = ThemeForm()

    return render(request, 'create_theme.html', {'theme_form': theme_form, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,})






def create_task(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.theme = theme
            task.save()
            return redirect('home')
    else:
        form = TaskForm()

    context = {
        'form': form,
        'theme': theme.id,
    }

    return render(request, 'create_theme.html', context)
