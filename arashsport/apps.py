from django.apps import AppConfig


class ArashsportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'arashsport'
    def ready(self):
        import arashsport.signals
