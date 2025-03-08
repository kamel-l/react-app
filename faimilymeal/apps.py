from django.apps import AppConfig

class FaimilymealConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faimilymeal'

    def ready(self):
        import members.signals  # Ceci va importer vos signaux


