from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Achievement(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class AchievementEarned(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, null=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    points = models.IntegerField(default=0)
    achievements = models.ManyToManyField(AchievementEarned)
    events_completed = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Theme(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class Task(models.Model):
    name = models.CharField(max_length=255)
    task = models.TextField()
    hint = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='tasks')
    secret_key = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    )
    PRIVACY_CHOICES = [
        ('P', 'Private'),
        ('U', 'Public'),
    ]
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(max_length=350)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=10)
    privacy = models.CharField(max_length=1, choices=PRIVACY_CHOICES, default='U')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='teams')
    points = models.IntegerField(default=0)

    class Meta:
        unique_together = ('name', 'event')

    def __str__(self):
        return self.name


class UserEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)


class TaskCompletion(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    # completed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    date_completed = models.DateTimeField(auto_now_add=True)


class Player(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    team = models.CharField(max_length=30, blank=False)
