# Generated by Django 5.1.1 on 2024-10-02 03:40

import streamada.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streamada', '0003_remove_video_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_file',
            field=models.FileField(upload_to='videos/', validators=[]),
        ),
    ]
