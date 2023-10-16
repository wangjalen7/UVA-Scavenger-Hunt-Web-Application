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
    path('create_scavenger_hunt/', views.create_scavenger_hunt, name='create_scavenger_hunt'),
    path('view_scavenger_hunts/', views.view_scavenger_hunts, name='view_scavenger_hunts'),
    path('manage_scavenger_hunts/', views.manage_scavenger_hunts, name='manage_scavenger_hunts'),
    path('approve_hunt/<int:hunt_id>/', views.approve_hunt, name='approve_hunt'),
    path('deny_hunt/<int:hunt_id>/', views.deny_hunt, name='deny_hunt'),
    path('publicevents/', views.ListScavengerHunt.as_view(), name='publicevents'),
    path('joinhunt/', views.join_hunt, name='joinhunt')
]

