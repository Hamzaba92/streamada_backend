# Generated by Django 5.1.1 on 2024-10-04 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streamada', '0006_alter_video_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='add_to_new_video_feed',
            field=models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='No', max_length=3),
        ),
    ]
