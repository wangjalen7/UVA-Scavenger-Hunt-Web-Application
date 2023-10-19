# Generated by Django 4.2.4 on 2023-10-17 04:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0002_event_hunttemplate_task_taskcompletion_team_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='privacy',
            field=models.CharField(choices=[('P', 'Private'), ('U', 'Public')], default='U', max_length=1),
        ),
    ]