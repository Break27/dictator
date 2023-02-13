from django.db import IntegrityError, transaction

from app.management.base import NonInteractiveCommand
from app.models import Language, ObjectTag


class Command(NonInteractiveCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help=''
        )
        parser.add_argument(
            '--description',
            help=''
        )
        parser.add_argument(
            '--tags', nargs='+',
            help=''
        )

    def handle(self, *args, **options):
        name = options['name']
        note = self.input('[Description] (blank): ', options['description'])
        tags = self.input('[Tags] (empty list): ', options['tags'])
        try:
            lang = Language(name=name, description=note)
            with transaction.atomic():
                lang.save()
                for tag_name in tags:
                    tag, created = ObjectTag.objects.get_or_create(name=tag_name, model=Language)
                    lang.tags.add(tag)
                    if created:
                        self.print("Created new Language Tag '%s'." % tag_name)
            self.print(self.style.SUCCESS("Successfully created Language '%s'.") % name)
        except IntegrityError:
            self.print_error(self.style.ERROR("ERROR: language '%s' already exists." % name))
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')
