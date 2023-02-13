from django.apps import AppConfig as Config
from django.conf import settings
from django.db import DatabaseError
from watson import search as watson


class AppConfig(Config):
    default_auto_field = 'django.db.models.BigAutoField'
    application = None
    verbose_name = 'dictionary'
    name = 'app'

    base_dir = settings.BASE_DIR / 'app'
    node_dir = base_dir / 'jstoolchains'

    def ready(self):
        self.update()
        self.register_search_index()

    @staticmethod
    def update():
        """
        Update application status
        """
        from app.models import Application
        try:
            AppConfig.application = Application.objects.first()
        except DatabaseError:
            pass

    def register_search_index(self):
        watson.register(self.get_model('Word'), fields=('transcript', 'entries__paraphrase'))
        watson.register(self.get_model('Entry'), fields=('paraphrase',))
        watson.register(self.get_model('ExampleSentence'), fields=('transcript',))
