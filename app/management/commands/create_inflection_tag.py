from django.db import transaction

from app.management.base import NonInteractiveCommand
from app.models import InflectionClass, InflectionTag


class Command(NonInteractiveCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'class',
            help=''
        )
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
            clss = InflectionClass.objects.get_or_create(name=options['class'])
        except InflectionClass.DoesNotExist:
            self.print_error("Inflection Class '%s' was not found." % options['class'])
            exit(1)

        try:
            with transaction.atomic():
                tag = InflectionTag(name=options['name'], clss=clss)
                tag.note = self.input('[Note] (blank): ', options['note'])
                tag.save()
            self.print(self.style.SUCCESS('Successfully created Inflection Tag.'))
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')
