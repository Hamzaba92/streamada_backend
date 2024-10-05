from django.db import models
from django.core.exceptions import ValidationError
import os
from django.conf import settings
from rest_framework import serializers




GENRE_CHOICES = [
    ('New', 'New on Streamada'),
    ('Sport', 'Sport'),
    ('Explore', 'Explore'),
    ('Western', 'Western'),
    ('Crime', 'Crime'),
    ('Abstract', 'Abstract'),
]



class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=360, blank=True, null=True)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    video_file = models.FileField(upload_to='videos/', validators=[])
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    add_to_new_video_feed = models.BooleanField(default=False)

    def __str__(self):
        return f"[Genre]: {self.genre},  [Title]: {self.title}"
    

    def save(self, *args, **kwargs):
        """Ensure validation is called before saving."""
        self.full_clean() 
        super(Video, self).save(*args, **kwargs)


    def get_video_version_url(self, resolution):
        base_name = os.path.splitext(self.video_file.name)[0]
        version_filename = f"{base_name}_{resolution}.mp4"
        return f"{settings.MEDIA_URL}{version_filename}"

    @property
    def video_480p_url(self):
        return self.get_video_version_url('480p')

    @property
    def video_720p_url(self):
        return self.get_video_version_url('720p')

    @property
    def video_1080p_url(self):
        return self.get_video_version_url('1080p')
    
    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return ''




