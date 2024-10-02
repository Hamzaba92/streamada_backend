from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from streamada.models import Video
import os

from streamada.tasks import convert_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print('New Video created')


        video_base_path = instance.video_file.path.replace('.mp4', '')
        versions = ['_480p.mp4', '_720p.mp4', '_1080p.mp4']
        for version in versions:
            version_path = video_base_path + version
            if os.path.isfile(version_path):
                raise ValueError(f"The file '{version_path}' already exists. Please remove it before uploading a new video.")

        convert_video(instance.video_file.path, 'hd480', '480p')
        convert_video(instance.video_file.path, 'hd720', '720p')
        convert_video(instance.video_file.path, 'hd1080', '1080p')

    """Delet's the uploadfile in raw"""
    if os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)



@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, *args, **kwargs):
    """Delete all 3 versions and the Thumbnail from the system"""

    video_base_path = instance.video_file.path.replace('.mp4', '')
    versions = ['_480p.mp4', '_720p.mp4', '_1080p.mp4']
    for version in versions:
        version_path = video_base_path + version
        if os.path.isfile(version_path):
            os.remove(version_path)
        
        if instance.thumbnail:
            if os.path.isfile(instance.thumbnail.path):
                os.remove(instance.thumbnail.path)
            