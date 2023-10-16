from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class ScavengerHunt(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=10)
    privacy = models.CharField(max_length=30, default="private")

    def __str__(self):
        return self.name
