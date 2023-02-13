from django.db import transaction

from app.management.base import NonInteractiveCommand, QuestionCommand
from app.models import Word, Language


class Command(NonInteractiveCommand, QuestionCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'language',
            help=''
        )
        parser.add_argument(
            'word',
            help=''
        )
        parser.add_argument(
            '--unicode',
            help=''
        )

    def handle(self, *args, **options):
        word_name = options['word']
        code = self.input('[Unicode] (blank): ', options['unicode'])
        try:
            lang = Language.objects.get(name=options['language'])
        except Language.DoesNotExist:
            self.print_error(self.style.ERROR("ERROR: Language '%s' was not found." % options['lang']))
            exit(1)

        try:
            while True:
                with transaction.atomic():
                    word = Word(transcript=word_name, language=lang, unicode=code)
                    word.save()
                self.print("Successfully created word '%s' in %s." % (word_name, lang))
                if self.interactive and self.question('Continue creating?'):
                    word_name = self.input('[word]: ')
                    continue
                break
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')
