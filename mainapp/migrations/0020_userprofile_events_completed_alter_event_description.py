<<<<<<<< HEAD:mainapp/migrations/0019_userprofile_events_completed_alter_event_description.py
# Generated by Django 4.2.4 on 2023-11-29 00:24
========
# Generated by Django 4.2.4 on 2023-11-29 00:27
>>>>>>>> 17851372ca11fa999ecca211b67cc602c7d354c2:mainapp/migrations/0020_userprofile_events_completed_alter_event_description.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0019_userprofile_events_completed_alter_event_description'),
    ]

    operations = [
<<<<<<<< HEAD:mainapp/migrations/0019_userprofile_events_completed_alter_event_description.py
        migrations.AddField(
            model_name='userprofile',
            name='events_completed',
            field=models.IntegerField(default=0),
        ),
========

>>>>>>>> 17851372ca11fa999ecca211b67cc602c7d354c2:mainapp/migrations/0020_userprofile_events_completed_alter_event_description.py
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(max_length=350),
        ),
    ]
