from django.db import transaction

from app.management.base import NonInteractiveCommand, VerboseCommand
from app.models import ExampleSentence


class Command(NonInteractiveCommand, VerboseCommand):
    interactive_help = 'Must have a sentence argument with --noinput.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'entry_id', type=int,
            help='Specify target entry with id.'
        )
        parser.add_argument(
            'sentence',
            help='Example sentence.'
        )
        parser.add_argument(
            '--note',
            help='Note for this sentence.'
        )
        parser.add_argument(
            '--unicode',
            help='Unicode for this sentence.'
        )

    def handle(self, *args, **options):
        try:
            example = ExampleSentence(entry_id=options['entry_id'], transcript=options['sentence'])
            note = self.input('[Note] (blank): ', options['note']).strip()
            code = self.input('[Unicode] (blank): ', options['unicode']).strip()

            with transaction.atomic():
                example.note = note
                example.unicode = code
                example.save()
            self.print(self.style.SUCCESS('Successfully created Example Sentence.'))
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')
