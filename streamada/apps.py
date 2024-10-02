from django.apps import AppConfig


class StreamadaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'streamada'

    def ready(self):
        from . import signals