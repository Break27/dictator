from django.db import transaction

from app.management.base import NonInteractiveCommand
from app.models import InflectionClass


class Command(NonInteractiveCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help=''
        )
        parser.add_argument(
            '--note',
            help=''
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                clss = InflectionClass(name=options['name'])
                clss.note = self.input('[note] (blank): ', options['note'])
                clss.save()
            self.print(self.style.SUCCESS("Successfully created Inflection Class."))
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')