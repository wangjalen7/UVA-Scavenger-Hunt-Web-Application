from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from .forms import EventForm, JoinEventForm, ThemeForm
from .models import Event, Player
=======
from .forms import EventForm, JoinEventForm, TaskForm, ThemeForm, TaskFormSet, JoinTeamForm, CreateTeamForm
from .models import Event, Player, Theme, Task, Team
>>>>>>> create/view-tasks
from allauth.account.views import SignupView
from .forms import AllauthCustomSignupForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
import logging
from django.contrib import messages
from django.http import HttpResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ScavengerHuntApp')



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


class CustomSignupView(SignupView):
    form_class = AllauthCustomSignupForm
    template_name = 'account/signup.html'


<<<<<<< HEAD
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
=======
def create_theme(request):
    if request.method == 'POST':
        form = ThemeForm(request.POST)
        formset = TaskFormSet(request.POST, queryset=Task.objects.none())
        if form.is_valid() and formset.is_valid():
            theme = form.save()
            tasks = formset.save(commit=False)
            for task in tasks:
                task.save()
                theme.tasks.add(task)
            return redirect('create_event')
>>>>>>> create/view-tasks
    else:
        form = ThemeForm()
        formset = TaskFormSet(queryset=Task.objects.none())
    return render(request, 'create_theme.html', {'form': form, 'formset': formset})




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


<<<<<<< HEAD
=======
@login_required
def event_details(request, event_id, tab='about'):
    event = Event.objects.get(pk=event_id)
    # Check if the user is a member of any team in this event
    is_member = Team.objects.filter(event=event, members=request.user).exists()
    teams = Team.objects.filter(event=event)
    context = {
        'event': event,
        'is_member': is_member,
        'tab': tab,
        'teams': teams,
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

    # Check if the user is already a member of this team
    if team_to_join.members.filter(id=request.user.id).exists():
        return render(request, 'error.html', context = {'message': 'You have already joined this team'})

    # Check if the user is a member of any other team in this event
    current_team = Team.objects.filter(event=event, members=request.user).first()
    if current_team:
        # Remove the user from the current team and add to the new team
        current_team.members.remove(request.user)
        team_to_join.members.add(request.user)
        messages.success(request, "You have switched to a new team.")
    else:
        # Add the user to the new team
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
    

    if Team.objects.filter(members=request.user).exists():
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

>>>>>>> create/view-tasks
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

<<<<<<< HEAD

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
=======
def create_task(request, theme_id):
    hunt = get_object_or_404(Theme, theme=theme_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            hunt.tasks.add(task)
            return redirect(reversed('task-list'))
    else:
        form = TaskForm()

    context = {
        'form': form,
        'hunt': hunt,
    }

    return render(request, 'task_form.html', context)
>>>>>>> create/view-tasks

