from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0019_userprofile_events_completed_alter_event_description'),
    ]

    operations = [
        ('mainapp', '0018_merge_20231112_0433'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='events_completed',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(max_length=350),
        ),
    ]
