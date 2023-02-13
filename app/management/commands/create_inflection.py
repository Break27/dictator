from app.management.base import NonInteractiveCommand


class Command(NonInteractiveCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'word',
            help=''
        )
        parser.add_argument(
            'inflection',
            help=''
        )
        parser.add_argument(
            'tags', nargs='+',
            help=''
        )

    def handle(self, *args, **options):
        pass
