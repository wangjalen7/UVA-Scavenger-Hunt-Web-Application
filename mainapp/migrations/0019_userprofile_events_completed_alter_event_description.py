# Generated by Django 4.2.4 on 2023-11-29 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_merge_20231112_0433'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='events_completed',
            field=models.IntegerField(default=0),
        ),
    ]