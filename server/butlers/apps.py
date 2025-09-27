from django.apps import AppConfig


class ButlersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'butlers'

    def ready(self):
        import butlers.signals