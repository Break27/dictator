from abc import ABC
from subprocess import Popen, PIPE

from django.core.management import BaseCommand as DjangoBaseCommand


class BaseCommand(DjangoBaseCommand, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print(self, *args, **kwargs):
        self.stdout.write(*args, **kwargs)

    def print_error(self, *args, **kwargs):
        self.stderr.write(*args, **kwargs)

    def input(self, prompt=''):
        return input(prompt)


class NonInteractiveCommand(BaseCommand, ABC):
    interactive_help = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactive = True

    def input(self, prompt='', default=''):
        if not self.interactive and default is None:
            raise ValueError("Argument 'default' must not be None while running in non-interactive mode.")
        return default or input(prompt)

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.add_argument(
            '--noinput', '--no-input', dest='interactive', action='store_false',
            help='Non-interactive mode. %s' % self.interactive_help
        )
        return parser

    def execute(self, *args, **options):
        self.interactive = options['interactive']
        return super().execute(*args, **options)


class VerboseCommand(BaseCommand, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbosity = 1

    def print(self, *args, level=1, **kwargs):
        if self.verbosity >= level:
            super().print(*args, **kwargs)

    def print_error(self, *args, level=1, **kwargs):
        if self.verbosity >= level:
            super().print_error(*args, **kwargs)

    def execute(self, *args, **options):
        self.verbosity = options['verbosity']
        return super().execute(*args, **options)


class QuestionCommand(BaseCommand, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.possible_response = ('yes', 'no', 'y', 'n', '')

    def question(self, prompt=''):
        prompt = (prompt + ' [Yes/No] (y): ').lstrip()
        while True:
            response = self.input(prompt).lower().strip()
            if response in self.possible_response:
                break
            self.print(self.style.ERROR(":: Invalid response '%s'." % response))

        return response != 'no' and response != 'n'


class RunProcessCommand(BaseCommand, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_process(self, *args, silent=False, wait=False, **kwargs):
        process = Popen(*args, **kwargs, stdout=PIPE, shell=True)
        if not silent:
            for line in iter(process.stdout.readline, b''):
                self.print(line)
        if wait:
            process.communicate()

        if process.poll():
            raise ChildProcessError('ERROR: Child process running failed.')

        return process.returncode
