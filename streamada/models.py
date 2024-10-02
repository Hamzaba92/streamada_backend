from django.db import models
from django.core.exceptions import ValidationError
import os

GENRE_CHOICES = [
    ('new_on_streamada', 'New on Streamada'),
    ('sport', 'Sport'),
    ('explore', 'Explore'),
    ('western', 'Western'),
    ('crime', 'Crime'),
    ('abstract', 'Abstract'),
]

def validate_video_file(value):
    """Validate the Uploadfile if its truly a videofile"""
    if not value.name.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise ValidationError("Only Videofiles which ends with '.mp4', '.mov', '.avi', '.mkv'")



class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    video_file = models.FileField(upload_to='videos/', validators=[validate_video_file])
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

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