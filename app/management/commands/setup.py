from django.core.management import call_command
from django.db import transaction, DatabaseError

from app.apps import AppConfig
from app.management.base import QuestionCommand, RunProcessCommand
from app.models import Application


class Command(QuestionCommand, RunProcessCommand):
    help = 'Initialize the application and run setup'
    version = '0.1.1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_dir = AppConfig.node_dir
        self.instance = AppConfig.application

    def handle_process(self, args, msg, error_msg, cwd=None):
        try:
            self.print(msg)
            self.run_process(args, silent=True, wait=True, cwd=cwd)
        except ChildProcessError:
            self.print_error(self.style.ERROR('ERROR: ' + error_msg))
            exit(1)

    def require(self, name, args):
        try:
            self.run_process(args, silent=True, wait=True)
        except ChildProcessError:
            self.print('Missing required package: ' + name)
            self.print('You may have to manually install it to proceed.')
            exit(1)

    def add_arguments(self, parser):
        parser.add_argument(
            '--gui',
            action='store_true',
            help='Set up graphical interface.'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Erase previously stored application data and run setup.'
        )

    def handle(self, *args, **options):
        self.print(self.style.HTTP_INFO('DICTATOR Setup Program // Application Version: ' + self.version))
        self.print('Performing system environment checks...')
        try:
            if options['clean']:
                self.print(self.style.WARNING('\nRunning setup on clean mode.'))
                self.print(':: This operation will wipe out all application data.')
                self.print(":: Note: this will not empty the database. Only the application's")
                self.print('::       configuration data are affected.')

                if self.question('Are you sure?'):
                    if self.instance is None:
                        self.print('Application is already clean.')
                    else:
                        self.instance.delete()
                        self.instance = None
                        self.print('App config erased.')
                else:
                    self.print('Operation cancelled.')
                    exit(0)

            # gui / web mode setup
            if options['gui']:
                pass
            else:
                # check if nodejs is installed
                self.require('NodeJS', ['node', '-v'])
                # build static files
                self.handle_process(
                    ['npm', 'install'],
                    "Installing node packages...",
                    "Failed installing node packages.",
                    cwd=self.node_dir
                )
                self.handle_process(
                    ['npm', 'run', 'build'],
                    "Building static files...",
                    "Failed building static files.",
                    cwd=self.node_dir
                )

            if self.instance is None:
                # migrate database
                self.print('\nMigrating database...')
                call_command('makemigrations')
                call_command('migrate')

                # new app instance
                self.instance = Application()

                # create superuser
                self.print('\n:: Would you like to create a superuser right now?')
                if self.question():
                    call_command('createsuperuser')
                    self.print(self.style.SUCCESS('Successfully created user.'))
                else:
                    self.print('Skipping creating superuser.')

                # name the app
                self.print('\n:: Would you like to name the application?')
                self.print(':: You can change it later in dictator/settings.py')
                self.print(":: Example: Emily's dictionary")
                while len(self.instance.name) == 0:
                    name = self.input('[app_name] (dictator): ').strip()
                    if len(name) == 0:
                        # default
                        name = 'dictator'
                    self.print(':: Got name: ' + name)
                    if not self.question('Is that correct?'):
                        continue
                    self.instance.name = name
                    self.print(self.style.SUCCESS('Name set.'))

                with transaction.atomic():
                    self.instance.save()

                self.print(self.style.SUCCESS('All set.'))
                self.print("\nHINT: If you wish, you can apply language presets using 'manage.py makepresets'.")
                self.print('      It can create a few demonstrative entries quickly.')
                return

            self.print(self.style.NOTICE('Application has already been set up.'))
            self.print('Nothing to do.')
        except DatabaseError as ex:
            self.print_error(self.style.ERROR('ERROR: Database Error.'))
            if options['traceback']:
                raise ex
        except KeyboardInterrupt:
            self.print('\nAbort.')
