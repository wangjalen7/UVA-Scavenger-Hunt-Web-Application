# Generated by Django 4.2.6 on 2023-11-12 00:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_task_secret_key_alter_taskcompletion_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskcompletion',
            name='completed_by',
        ),
    ]