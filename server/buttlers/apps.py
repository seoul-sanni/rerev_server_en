from django.apps import AppConfig


class ButtlersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'buttlers'

    def ready(self):
        import buttlers.signals