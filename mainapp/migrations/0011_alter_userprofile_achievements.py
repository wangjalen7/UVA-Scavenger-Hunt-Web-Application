# Generated by Django 4.2.6 on 2023-11-08 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0010_userprofile_achievements"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="achievements",
            field=models.JSONField(default=list),
        ),
    ]