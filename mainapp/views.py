from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EventForm, TaskForm, ThemeForm, JoinTeamForm, CreateTeamForm, TaskFormSet
from .models import Event, Theme, Task, Team, UserProfile, Achievement, AchievementEarned, Player, UserEvent, \
    TaskCompletion
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
from django.conf import settings  # need api key from google to make the request
import datetime
import json

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
def hint_view(request, event_id, task_id):
    key = settings.GOOGLE_MAPS_API_KEY
    event = Event.objects.get(pk=event_id)
    task = Task.objects.get(pk=task_id)

    use_hint_achievement(request, request.user)

    return render(request, 'map.html',
                  {'key': key, 'latitude': task.latitude, 'longitude': task.longitude, 'hint': task.hint,
                   'name': task.name, 'event': event, })


class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'


@login_required
def profile(request):
    profile_error = ""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    user = request.user
    achievements = AchievementEarned.objects.filter(user=user)
    user_position = UserProfile.objects.filter(points__gt=user_profile.points).count() + 1
    signup_achievement(request, user)
    return render(request, 'profile/profile.html', {'user': user, 'achievements': achievements, 'user_position': user_position})


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

            change_name_achievement(request, user)

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

            change_description_achievement(request, request.user)
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
            create_hunt_achievement(request, request.user)
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
    return render(request, 'view_my_events.html', {'events': events, 'title': "My Events"})


@login_required
def event_about(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_event_member = UserEvent.objects.filter(event=event, user=request.user).exists()
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()
    context = {'event': event, 'is_event_member': is_event_member, 'is_team_member': is_team_member,
               'my_team': my_team, }
    return render(request, 'event_tabs/about.html', context)


@login_required
def event_leaderboard(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()
    teams = Team.objects.filter(event=event_id).order_by('-points')

    if my_team == teams[0]:
        win_event_achievement(request, request.user)

    context = {'event': event, 'is_team_member': is_team_member, 'my_team': my_team, 'teams': teams}
    return render(request, 'event_tabs/leaderboard.html', context)


@login_required
def event_tasks(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()
    # Filter tasks by the event's theme
    all_tasks = Task.objects.filter(theme=event.theme)

    completed_tasks_ids = TaskCompletion.objects.filter(team=my_team, task__theme=event.theme).values_list('task_id', flat=True)

    context = {
        'event': event,
        'is_team_member': is_team_member,
        'my_team': my_team,
        'all_tasks': all_tasks,
        'completed_tasks_ids': list(completed_tasks_ids),
    }
    return render(request, 'event_tabs/all_tasks.html', context)


@login_required
def event_teams(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    teams = Team.objects.filter(event=event)
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()
    context = {'event': event, 'teams': teams, 'is_team_member': is_team_member, 'my_team': my_team, }
    return render(request, 'event_tabs/teams.html', context)


@login_required
def event_team(request, event_id, team_id):
    event = get_object_or_404(Event, pk=event_id)
    team = get_object_or_404(Team, pk=team_id, event=event)
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()
    context = {'event': event, 'team': team, 'is_team_member': is_team_member, 'my_team': my_team, }
    return render(request, 'event_tabs/team.html', context)


@login_required
def event_tasks_todo(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()

    # Get the theme and all tasks for the event's theme
    all_tasks = Task.objects.filter(theme=event.theme)

    # Get completed tasks' IDs for the team
    completed_tasks_ids = TaskCompletion.objects.filter(team=my_team, task__theme=event.theme).values_list('task_id', flat=True)

    # Filter out completed tasks
    tasks_todo = all_tasks.exclude(id__in=completed_tasks_ids)

    context = {
        'event': event,
        'is_team_member': is_team_member,
        'my_team': my_team,
        'all_tasks': all_tasks,
        'tasks_todo': tasks_todo,
    }

    return render(request, 'event_tabs/tasks_todo.html', context)


@login_required
def event_completed_tasks(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_team_member = Team.objects.filter(event=event, members=request.user).exists()
    my_team = Team.objects.filter(event=event, members=request.user).first()
    all_tasks = Task.objects.filter(theme=event.theme)
    # Get IDs of tasks completed by the team
    completed_tasks_ids = TaskCompletion.objects.filter(team=my_team, task__theme=event.theme).values_list('task_id', flat=True)

    # Fetch completed tasks
    completed_tasks = Task.objects.filter(id__in=completed_tasks_ids)

    if completed_tasks.count() == all_tasks.count():
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        user_profile.events_completed += 1
        user_profile.save()

        if user_profile.events_completed == 5:
            five_events_achievement(request, request.user)
        if user_profile.events_completed == 10:
            ten_events_achievement(request, request.user)
        if user_profile.events_completed == 25:
            twentyfive_events_achievement(request, request.user)
        if user_profile.events_completed == 50:
            fifty_events_achievement(request, request.user)
        if user_profile.events_completed == 100:
            onehundred_events_achievement(request, request.user)

    context = {
        'event': event,
        'is_team_member': is_team_member,
        'all_tasks': all_tasks,
        'my_team': my_team,
        'completed_tasks': completed_tasks,
        'completed_task_ids': list(completed_tasks_ids),
    }

    return render(request, 'event_tabs/completed_tasks.html', context)


@login_required
def join_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Check if the user has already joined the event
    if UserEvent.objects.filter(user=request.user, event=event).exists():
        messages.error(request, "You have already joined this event.")
        return redirect('event_about', event_id=event_id)

    # Check if the event is public or if the user is allowed to join
    if event.privacy == 'U' or (event.privacy == 'P' and request.user in event.allowed_users):
        # Create UserEvent
        user_event = UserEvent(user=request.user, event=event)
        user_event.save()

        messages.success(request, "You have successfully joined the event.")
        return redirect('event_about', event_id=event_id)
    else:
        messages.error(request, "You are not allowed to join this event.")


@login_required
def leave_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user_event = UserEvent.objects.filter(user=request.user, event=event)

    if not user_event.exists():
        messages.error(request, "You are not part of this event.")
        return redirect('event_about', event_id=event_id)

    if request.method == 'POST':
        # Remove the user from any teams in this event
        teams = Team.objects.filter(event=event, members=request.user)
        for team in teams:
            team.members.remove(request.user)
            # If the team has no more members, delete the team
            if team.members.count() == 0:
                team.delete()

        # Delete the UserEvent instance
        user_event.delete()

        messages.success(request, "You have successfully left the event.")

    return redirect('event_about', event_id=event_id)


# @login_required
# def team_details(request, event_id, team_id):
#     event = get_object_or_404(Event, pk=event_id)
#     team = get_object_or_404(Team, pk=team_id, event=event)
#     members = team.members.all()
#     return render(request, 'event_details.html', {'event': event, 'team': team, 'members': members, 'tab': 'team'})


@login_required
def join_team(request, event_id, team_id):
    event = get_object_or_404(Event, pk=event_id)
    team_to_join = get_object_or_404(Team, pk=team_id, event=event)

    # Check if user is part of the event
    if not UserEvent.objects.filter(user=request.user, event=event).exists():
        messages.error(request, "You need to join the event before joining a team.")
        return redirect('event_about', event_id=event_id)

    # Check if user has already joined this team
    if team_to_join.members.filter(id=request.user.id).exists():
        messages.error(request, "You have already joined this team.")
        return redirect('event_team', event_id=event_id, team_id=team_id)

    # Check if user is part of another team in the same event
    current_team = Team.objects.filter(event=event, members=request.user).first()
    if current_team:
        current_team.members.remove(request.user)

    team_to_join.members.add(request.user)
    messages.success(request, "You have successfully joined the team.")
    # join_hunt_achievement(request.user)

    return redirect('event_team', event_id=event_id, team_id=team_id)


@login_required
def create_team(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is part of the event
    if not UserEvent.objects.filter(user=request.user, event=event).exists():
        messages.error(request, "You need to join the event before creating a team.")
        return redirect('event_about', event_id=event_id)

    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            new_team_name = form.cleaned_data['new_team_name']

            # Check if a team with the same name already exists for this event
            if Team.objects.filter(name=new_team_name, event=event).exists():
                messages.error(request, "A team with this name already exists in the event.")
                return redirect('create_team', event_id=event_id)

            new_team = Team.objects.create(name=new_team_name, event=event)
            new_team.members.add(request.user)
            messages.success(request, "Team created successfully.")
            create_team_achievement(request, request.user)
            return redirect('event_about', event_id=event_id)

    if Team.objects.filter(members=request.user, event=event).exists():
        messages.error(request, "You have already joined a team.")
        return redirect('event_team', event_id=event_id,
                        team_id=Team.objects.filter(members=request.user, event=event).first().id)

    create_team_form = CreateTeamForm()
    context = {
        'event': event,
        'create_team_form': create_team_form,
    }
    return render(request, 'create_team.html', context)



@login_required
def leave_team(request, event_id, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Check if user is part of the team
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, "You are not part of this team.")
        return redirect('event_about', event_id=event_id)

    if request.method == 'POST':
        team.members.remove(request.user)

        # Delete the team if this was the last member
        if team.members.count() == 0:
            team.delete()
            messages.success(request, "Team has been disbanded as you were the last member.")
        else:
            messages.success(request, "You have successfully left the team.")
    return redirect('event_about', event_id=event_id)


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
def leaderboard(request, ):
    leaders = User.objects.alias(
        total_points=Sum('userprofile__points')
    ).exclude(userprofile__points__isnull=True).order_by('-total_points')[:10]

    if request.user == leaders[0]:
        first_place_achievement(request, request.user)

    return render(request, 'leaderboard.html', {'leaders': leaders})


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
                    theme=theme,
                    secret_key = task_info.get('secret_key', '')
                )

            return redirect('home')

    else:
        theme_form = ThemeForm()

    return render(request, 'create_theme.html', {'theme_form': theme_form,
                                                 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY, })  # remember change here for key


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


def change_name_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Call Sign").exists():
        achievement = Achievement.objects.create(name="Call Sign", points=5, description="Changed username")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " - " + str(
            achievement.points) + "pts")


def change_description_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Traveler’s Journal").exists():
        achievement = Achievement.objects.create(name="Traveler’s Journal", points=5, description="Changed description")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " - " + str(
            achievement.points) + "pts")


def first_place_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Fame and Fortune").exists():
        achievement = Achievement.objects.create(name="Fame and Fortune", points=10,
                                                 description="Earned 1st place on leaderboard")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")


def join_hunt_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Up to the Challenge").exists():
        achievement = Achievement.objects.create(name="Up to the Challenge", points=5,
                                                 description="Joined 1st scavenger hunt")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")


def create_hunt_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Cartographer").exists():
        achievement = Achievement.objects.create(name="Cartographer", points=5,
                                                 description="Created 1st scavenger hunt")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")


def create_team_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Expedition Leader").exists():
        achievement = Achievement.objects.create(name="Expedition Leader", points=5, description="Created 1st team")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")


def signup_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Signing On").exists():
        achievement = Achievement.objects.create(name="Signing On", points=5, description="Successfully logged in")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")

def use_hint_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="SOS").exists():
        achievement = Achievement.objects.create(name="SOS", points=5, description="Used a hint")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")

def win_event_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Sweet Victory").exists():
        achievement = Achievement.objects.create(name="Sweet Victory", points=10, description="Won first scavenger hunt event")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")
        
def five_events_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="On the Hunt").exists():
        achievement = Achievement.objects.create(name="On the Hunt", points=5, description="Completed 5 scavenger hunt events")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")

def ten_events_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Searching for Treasure").exists():
        achievement = Achievement.objects.create(name="Searching for Treasure", points=10, description="Completed 10 scavenger hunt events")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")
        
def twentyfive_events_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Spirit of Adventure").exists():
        achievement = Achievement.objects.create(name="Spirit of Adventure", points=20, description="Completed 25 scavenger hunt events")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")
        
def fifty_events_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Map Genius").exists():
        achievement = Achievement.objects.create(name="Map Genius", points=30, description="Completed 50 scavenger hunt events")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")
        
def onehundred_events_achievement(request, user):
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    if not AchievementEarned.objects.filter(user=user, achievement__name="Super Searcher").exists():
        achievement = Achievement.objects.create(name="Super Searcher", points=50, description="Completed 100 scavenger hunt events")
        user_achievement = AchievementEarned(user=user, achievement=achievement)
        user_achievement.save()

        user_profile.points += user_achievement.achievement.points
        user_profile.achievements.add(user_achievement)
        user_profile.save()
        messages.info(request, "Achievement earned! " + achievement.name + ": " + achievement.description + " +" + str(
            achievement.points) + "pts")

@login_required
def check_task_secret_key(request, event_id, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id)
        event = get_object_or_404(Event, pk=event_id)
        my_team = Team.objects.filter(event=event, members=request.user).first()

        entered_key = request.POST.get('secret_key')
        print("Entered key:", entered_key)  # Debugging
        print("Actual key:", task.secret_key)  # Debugging

        if task.secret_key == entered_key:
            # Check if the task has already been completed by the team
            completion, created = TaskCompletion.objects.get_or_create(task=task, team=my_team)
            if created:
                my_team.points += 5
                my_team.save()

                request.user.userprofile.points += 5
                request.user.userprofile.save()
                messages.success(request, 'Task completed successfully! You earned 5 points.')
            else:
                messages.warning(request, 'You have already completed this task.')
        else:
            messages.error(request, 'Incorrect secret key!')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('event_tasks_todo', event_id=event_id)




