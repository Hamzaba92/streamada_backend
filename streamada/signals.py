from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from streamada.models import Video
import os
import django_rq
from streamada.tasks import convert_video, delete_original_file



@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print('New Video created')

        video_base_path = (instance.video_file.path.replace('.mp4', ''))
        versions = ['_480p.mp4', '_720p.mp4', '_1080p.mp4']

        for version in versions:
            version_path = video_base_path + version
            if os.path.isfile(version_path):
                raise ValueError(f"The file '{version_path}' already exists. Please remove it before uploading a new video.")

        # RQ-Queue, get the default worker
        queue = django_rq.get_queue('default')

        # manage the queue
        video_path = (instance.video_file.path)
        job_480p = queue.enqueue(convert_video, video_path, 'hd480', '480p')
        job_720p = queue.enqueue(convert_video, video_path, 'hd720', '720p', depends_on=job_480p)
        job_1080p = queue.enqueue(convert_video, video_path, 'hd1080', '1080p', depends_on=job_720p)

        queue.enqueue(delete_original_file, video_path, depends_on=job_1080p)





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
            