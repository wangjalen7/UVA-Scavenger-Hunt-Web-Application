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
from mainapp.views import index
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.urls import path
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),  # Use the index view here
    path('accounts/', include('allauth.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', TemplateView.as_view(template_name="register.html"), name='register'),
    path('home/', TemplateView.as_view(template_name="home.html"), name='home'),
    path('create_event/', views.create_event, name='create_event'),
    path('view_public_events/', views.view_public_events, name='view_public_events'),
    path('view_my_events/', views.view_my_events, name='view_my_events'),
    path('manage_events/', views.manage_events, name='manage_events'),
    path('approve_hunt/<int:event_id>/', views.approve_event, name='approve_event'),
    path('deny_hunt/<int:event_id>/', views.deny_event, name='deny_event'),
    #path('publicevents/', views.ListScavengerHunt.as_view(), name='public_events'),
    path('join_event/<int:event_id>', views.join_event, name='join_event'),
    path('create-theme/', views.create_theme, name='create_theme'),
    path('create_task/', views.create_task, name='create_task'), 
]

