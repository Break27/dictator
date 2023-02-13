from django.core.management import call_command, CommandError
from django.db import transaction

from app.management.base import NonInteractiveCommand, VerboseCommand, QuestionCommand
from app.models import Language, Word, WordClass, Entry, ObjectTag


class Command(NonInteractiveCommand, VerboseCommand, QuestionCommand):
    interactive_help = 'Must have --paraphrase with --noinput.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry_id = None

    def find_object(self, model, *args, **kwargs):
        name = kwargs.get('name') or kwargs.get('transcript')
        try:
            instance = model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            self.print_error(self.style.ERROR("ERROR: %s '%s' was not found." % (model.__name__, name)))
            exit(1)
        return instance

    def validate_input(self, prompt, error_msg):
        while True:
            trim = input(prompt).strip()
            if len(trim) > 0:
                return trim
            self.print_error(self.style.ERROR(error_msg))

    def add_arguments(self, parser):
        parser.add_argument(
            'language',
            help='Specify target Language.'
        )
        parser.add_argument(
            'word',
            help='Target Word for this entry.'
        )
        parser.add_argument(
            'word_class',
            help="Target Word Class for this entry. Use Word Class fullname."
        )
        parser.add_argument(
            '--paraphrase',
            help='Paraphrase of this Entry.'
        )
        parser.add_argument(
            '--note',
            help='Note for this Entry.'
        )
        parser.add_argument(
            '--tags', dest='tags', nargs='+',
            help='Add tags to this Entry. A new tag will be created if it was not found.'
        )

    def execute(self, *args, **options):
        if not self.interactive and not options['paraphrase']:
            raise CommandError('Must have --paraphrase in non-interactive mode.')
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        try:
            lang = self.find_object(Language, name=options['language'])
            word = self.find_object(Word, transcript=options['word'], language=lang)
            clss = self.find_object(WordClass, name=options['word_class'])

            self.print(
                ":: Creating an Entry for Word '%s' (%s class) in Language '%s'."
                % (word.transcript, clss.name, lang.name)
            )
            entry = Entry(word=word, word_class=clss)

            paraphrase = options['paraphrase'] or self.validate_input(
                '[Paraphrase]: ',
                'An entry requires at least one paraphrase.'
            )
            note = self.input('[Note] (blank): ', options['note']).strip()
            tags = self.input('[Tags] (empty list): ', options['tags'])

            if isinstance(tags, str) and len(tags) > 0:
                tags = tags.strip().split(' ')

            with transaction.atomic():
                entry.paraphrase = paraphrase
                entry.note = note
                entry.save()

                for name in tags:
                    tag, created = ObjectTag.objects.get_or_create(name=name, model=Entry)
                    if created:
                        self.print("Created new Entry Tag '%s'." % name)
                    entry.tags.add(tag)

            self.print(self.style.SUCCESS('Successfully created Entry (id: %s).' % entry.id))
            self.entry_id = entry.id

            if self.interactive:
                self.print(':: Do you wish to add an Example Sentence to the Entry right now?')
                if self.question():
                    while True:
                        sentence = self.validate_input(
                            '[Sentence]: ',
                            'At least one sentence is required.'
                        )
                        call_command('create_sentence', entry.id, sentence, verbosity=self.verbosity)

                        if not self.question('Continue adding?'):
                            break
                    self.print(self.style.SUCCESS('All sentence(s) added.'))
                else:
                    self.print('Skipping adding Example Sentences.')
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')
