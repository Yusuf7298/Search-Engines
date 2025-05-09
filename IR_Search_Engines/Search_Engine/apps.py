from django.apps import AppConfig
import nltk

class SearchEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Search_Engine'

    def ready(self):
        from . import signals
        signals.register_signals()
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)