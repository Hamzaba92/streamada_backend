from django.db import models
from django.core.exceptions import ValidationError

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