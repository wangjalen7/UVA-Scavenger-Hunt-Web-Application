from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    # profile_pic

    def __str__(self):
        return self.user.username

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class HuntTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    tasks = models.ManyToManyField(Task) 
    theme = models.CharField(max_length=255)

class Event(models.Model):
    PRIVACY_CHOICES = [
        ('P', 'Private'),
        ('U', 'Public'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    template = models.ForeignKey(HuntTemplate, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    privacy = models.CharField(max_length=1, choices=PRIVACY_CHOICES)


class Team(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='teams')

class UserEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

class TaskCompletion(models.Model):
    task = models.CharField(max_length=255)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    date_completed = models.DateTimeField(auto_now_add=True)




