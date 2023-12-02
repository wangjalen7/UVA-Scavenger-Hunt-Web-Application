"""
URL configuration for ScavengerHuntApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.urls import path
from mainapp import views
from mainapp.views import check_task_secret_key

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', TemplateView.as_view(template_name="index.html"), name='home'),  # Use the index view here
    path('accounts/', include('allauth.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', TemplateView.as_view(template_name="register.html"), name='register'),

    path('profile/', views.profile, name='profile'),
    path('profile/change_username/', views.change_username, name='change_username'),
    path('profile/change_bio/', views.change_bio, name='change_bio'),
    path('create_event/', views.create_event, name='create_event'),
    path('', views.view_public_events, name='home'),
    path('view_my_events/', views.view_my_events, name='view_my_events'),
    path('manage_events/', views.manage_events, name='manage_events'),
    path('approve_hunt/<int:event_id>/', views.approve_event, name='approve_event'),
    path('deny_hunt/<int:event_id>/', views.deny_event, name='deny_event'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('approve_event/<int:event_id>/', views.approve_event, name='approve_event'),
    path('deny_event/<int:event_id>/', views.deny_event, name='deny_event'),
    path('create_task/<int:theme_id>', views.create_task, name='create_task'),
    path('create_theme/', views.create_theme, name='create_theme'),
    path('event/<int:event_id>/hint/<int:task_id>', views.hint_view, name="hint"),

    path('event/<int:event_id>/', views.event_about, name='event_about'),  # Default to 'about' tab
    path('event/<int:event_id>/leaderboard/', views.event_leaderboard, name='event_leaderboard'),
    path('event/<int:event_id>/tasks/', views.event_tasks, name='event_tasks'),  # All tasks
    path('event/<int:event_id>/teams/', views.event_teams, name='event_teams'),
    path('event/<int:event_id>/team/<int:team_id>', views.event_team, name='event_team'),  # My team
    path('event/<int:event_id>/all_tasks', views.event_tasks, name='event_all_tasks'),
    path('event/<int:event_id>/tasks/todo/', views.event_tasks_todo, name='event_tasks_todo'),
    path('event/<int:event_id>/tasks/completed/', views.event_completed_tasks, name='event_completed_tasks'),

    path('event/<int:event_id>/join/', views.join_event, name='join_event'),
    path('event/<int:event_id>/leave/', views.leave_event, name='leave_event'),
    path('event/<int:event_id>/create_team/', views.create_team, name='create_team'),
    path('event/<int:event_id>/leave_team/<int:team_id>', views.leave_team, name='leave_team'),
    path('event/<int:event_id>/team/<int:team_id>/join/', views.join_team, name='join_team'),

    path('achievement/', views.change_name_achievement, name='achievement'),

    path('event/<int:event_id>/task/<int:task_id>/check_key/', check_task_secret_key, name='check_task_secret_key'),

]
