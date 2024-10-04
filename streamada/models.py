from django.db import models
from django.core.exceptions import ValidationError
import os
from django.conf import settings


GENRE_CHOICES = [
    ('New', 'New on Streamada'),
    ('Sport', 'Sport'),
    ('Explore', 'Explore'),
    ('Western', 'Western'),
    ('Crime', 'Crime'),
    ('Abstract', 'Abstract'),
]

def validate_video_file(value):
    """Validate the Uploadfile if its truly a videofile"""
    if not value.name.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise ValidationError("Only Videofiles which ends with '.mp4', '.mov', '.avi', '.mkv'")



class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=480, blank=True, null=True)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    video_file = models.FileField(upload_to='videos/', validators=[validate_video_file])
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    add_to_new_video_feed = models.BooleanField(default=False)


    def __str__(self):
        return f"[Genre]: {self.genre},  [Title]: {self.title}"
    

    def clean(self):
        """
        Custom validation to check if a video or thumbnail with the same name already exists.
        """
        if Video.objects.filter(video_file=self.video_file.name).exists():
            raise ValidationError(f"The video file '{self.video_file.name}' already exists.")

        video_path = os.path.join('media/videos', self.video_file.name)
        if os.path.exists(video_path):
            raise ValidationError(f"The file '{self.video_file.name}' already exists on the server.")

        if self.thumbnail:
            if Video.objects.filter(thumbnail=self.thumbnail.name).exists():
                raise ValidationError(f"The thumbnail '{self.thumbnail.name}' already exists.")
            
            thumbnail_path = os.path.join('media/thumbnails', self.thumbnail.name)
            if os.path.exists(thumbnail_path):
                raise ValidationError(f"The file '{self.thumbnail.name}' already exists on the server.")


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




