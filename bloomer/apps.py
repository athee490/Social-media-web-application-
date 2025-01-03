from django.apps import AppConfig


class BloomerConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bloomer'
    def ready(self):
        import bloomer.signals

