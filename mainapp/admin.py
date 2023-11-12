from django.contrib import admin
from .models import Event, Theme, Task, TaskCompletion

# Register your models here.
admin.site.register(Event)
admin.site.register(Theme)
admin.site.register(Task)
admin.site.register(TaskCompletion)