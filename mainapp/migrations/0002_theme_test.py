# Generated by Django 4.2.3 on 2023-10-31 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='test',
            field=models.TextField(default='hello'),
            preserve_default=False,
        ),
    ]
