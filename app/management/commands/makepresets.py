import sys
from argparse import Action, SUPPRESS

from django.db import IntegrityError, DatabaseError, transaction

from app.management.base import BaseCommand
from app.models import Language, ObjectTag, Word, WordClass, Entry, ExampleSentence


class Command(BaseCommand):
    _avail_presets = {
        'epo': 'Esperanto',
        'klg': 'Klingon',
        'sda': 'Sindarin',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.preset_applied = []

    class _PresetApplyingFunctions:
        Noun = 'Noun/n'
        Verb = 'Verb/v'
        Pron = 'Pronoun/pron'
        Conj = 'Conjunction/conj'
        Adj = 'Adjective/adj'
        Adv = 'Adverb/adv'

        def __init__(self):
            self.language = None

        def create_entry(self, word, clss, entry, sentences=None):
            clss, abbr = clss.split('/')
            tags = entry.setdefault('tags', [])

            word_class, _ = WordClass.objects.get_or_create(
                name=clss, abbr=abbr
            )
            word, _ = Word.objects.get_or_create(
                transcript=word, language=self.language
            )
            entry = Entry(
                word=word,
                word_class=word_class,
                paraphrase=entry.get('para'),
                note=entry.setdefault('note', ''),
            )
            entry.save()

            for name in tags:
                tag, _ = ObjectTag.objects.get_or_create(name=name, model='Entry')
                entry.tags.add(tag)

            if sentences is not None:
                for item in sentences:
                    example = ExampleSentence(
                        entry=entry,
                        transcript=item.get('sent'),
                        unicode=item.setdefault('code', ''),
                        note=item.setdefault('note', ''),
                    )
                    example.save()

        def create_lang(self, name, note, tags=None):
            lang = Language(name=name, description=note)
            lang.save()
            if tags is not None:
                for name in tags:
                    tag, _ = ObjectTag.objects.get_or_create(name=name, model=Language)
                    lang.tags.add(tag)
            self.language = lang

        def _epo_(self):
            """
            Preset Esperanto

            Description from https://wikipedia.org.

            Paraphrases and examples are from https://vortaro.net.
            """
            self.create_lang(
                'Esperanto',
                'Origine la Lingvo Internacia, estas la plej disvasti??inta internacia planlingvo.'
            )
            self.create_entry(
                'abomeno', self.Noun, {
                    'para': 'Forta antipatio, ka??zata de tre malagrablaj a?? malnoblaj ecoj de objekto, persono a?? ago'
                }, [
                    {'sent': '??i sentis e?? ian abomenon kontra?? man??ado'},
                    {'sent': 'Se okazas al mi ekvidi ekzemple ian karoan re??on, tiam atakas min tia abomeno, ke mi '
                             'simple kra??as!'}
                ]
            )
            self.create_entry(
                'kordo', self.Noun, {
                    'para': 'Fadeno el bestaj intestoj, plasto, silko a?? metalo por muzikaj instrumentoj, '
                            'kiun stre??itan oni vibrigas jen per fingroj (gitaro, harpo), jen per ar??o (violono), '
                            'jen per marteletoj (piano)',
                    'tags': ['Muziko']
                }, [
                    {'sent': 'La ar??o kuradis tien k reen super la kordoj'},
                    {'sent': 'La propono tu??is kordon (animan inklinon) de ni mem ??is hodia?? ne rimarkitan'}
                ]
            )
            self.create_entry(
                'pargeto', self.Noun, {
                    'para': 'Ligna planko, konsistanta el simetrie k varie kunmetitaj tabuletoj el malmola k polurita '
                            'ligno',
                    'tags': ['Konstrutekniko']
                }
            )
            self.create_entry(
                'klapo', self.Noun, {
                    'para': 'Peco el ??ia ajn materialo, artikigita ??enerale en unu el siaj finoj k libere svingebla '
                            'en la dua'
                }, [
                    {'sent': 'Klapo de tablo, de ??apo, de maniko'}
                ]
            )
            self.create_entry(
                'klapo', self.Noun, {
                    'para': '??iu el du klapoformaj partoj de ??us dehiskinta antero de iaj stamenoj.',
                    'tags': ['Botaniko']
                }, [
                    {'sent': 'Valvo, operkulo.'}
                ]
            )
            self.create_entry(
                'klapo', self.Noun, {
                    'para': '??iu el la moveblaj pecoj, per kiu oni malfermas a?? fermas la truojn de iuj '
                            'blovinstrumentoj',
                    'tags': ['Muziko']
                }, [
                    {'sent': 'Vi volas ludi sur mi, vi pensas, ke vi konas miajn klapojn'}
                ]
            )
            self.create_entry(
                'polvo', self.Noun, {
                    'para': 'Aro da subtilaj liberaj eretoj de substanco, facile disi??antaj'
                }, [
                    {'sent': 'Diamanta polvo'},
                    {'sent': 'La vento ??etis al ni polvon da akvo'}
                ]
            )
            self.create_entry(
                'polvo', self.Noun, {
                    'para': 'Tiaj eretoj el tero a?? alia substanco al ??i miksita, ku??antaj sur la grundo a?? levataj de '
                            'la vento'
                }, [
                    {'sent': 'La ringo falis en la polvon'},
                    {'sent': 'Ili ??etis polvon sur siajn kapojn'},
                    {'sent': '??eti, ??uti al iu polvon en la okulojn'}
                ]
            )
            self.create_entry(
                'polvo', self.Noun, {
                    'para': 'Tiaj eretoj, kiuj kolekti??as kun malpura??oj en la domoj'
                }, [
                    {'sent': 'Vi??i la polvon de sur la mebloj'},
                ]
            )
            self.create_entry(
                'polvo', self.Noun, {
                    'para': 'Resta??oj de homa korpo',
                }, [
                    {'sent': 'Vi ka??as en vi la polvon de Holberg'}
                ]
            )
            self.create_entry(
                'gofri', self.Verb, {
                    'para': 'Enpremi per varma ilo (mal)reliefajn ornama??ojn (ondumetojn, krispojn, kanelojn ks) sur '
                            'paperon, ledon, puntojn ks'
                }, [
                    {'sent': 'Gofritaj randoj de librobinda??o.'}
                ]
            )
            self.create_entry(
                'kamufli', self.Verb, {
                    'para': 'Maski militobjekton, donante al ??i la aspekton, koloron a?? formon de la ??irka??a??oj',
                    'tags': ['Armeoj']
                }, [
                    {'sent': 'La aviadisto ne povis distingi la kamuflitajn kanonojn.'}
                ]
            )
            self.create_entry(
                'knedi', self.Verb, {
                    'para': 'Premadi k prilabori per la manoj pastecan substancon, por doni al ??i ian formon'
                }, [
                    {'sent': 'Princo bela knedita el mildo k pla??o'},
                    {'sent': 'Knedi (masa??i) la muskolojn'}
                ]
            )
            self.create_entry(
                'perturbi', self.Verb, {
                    'para': 'Ka??zi malordon'
                }, [
                    {'sent': 'Perturbita digestado, televida ricevado'}
                ]
            )
            self.create_entry(
                'razi', self.Verb, {
                    'para': 'Fortran??i la harojn ??e la ha??to per tiucela ilo'
                }, [
                    {'sent': 'Estas hontinde por virino esti kun haroj tonditaj a?? razitaj'},
                    {'sent': 'Razi al iu la barbon'}
                ]
            )
            self.create_entry(
                'elstara', self.Adj, {
                    'para': 'Tia, ke ??i elstaras'
                }, [
                    {'sent': 'Elstara balkono, fenestro'}
                ]
            )
            self.create_entry(
                'elstara', self.Adj, {
                    'para': 'Eminenta'
                }, [
                    {'sent': 'Plej elstaraj artistoj'},
                    {'sent': 'Montri elstaran heroecon'}
                ]
            )
            self.create_entry(
                'abrupta', self.Adj, {
                    'para': 'Malagrable subita, ne??entile senprepara'
                }, [
                    {'sent': '(ordoni) Per rapida, abrupta vo??o'}
                ]
            )
            self.create_entry(
                'sagitala', self.Adj, {
                    'para': '(sagittalis) Situanta en, a?? paralela al, la vertikala simetria ebeno (pasanta la??longe '
                            'tra la spino)',
                    'tags': ['Anatomio kaj histologio']
                }, [
                    {'sent': 'Sagitala sekca??o'},
                    {'sent': 'Sagitala diametro de la pelvo'}
                ]
            )
            self.create_entry(
                'private', self.Adv, {
                    'para': 'En privata maniero'
                }, [
                    {'sent': 'Mia projekto prezentas ja ne ian private faritan decidon'},
                    {'sent': '(sciigojn) Mi donas al vi ne kiel publikigotan leteron, sed nur private'}
                ]
            )
            self.create_entry(
                'sume', self.Adv, {
                    'para': 'Adiciante ??ion'
                }, [
                    {'sent': 'Tiom por la voja??o, tiom por la man??o, tiom por la lo??ado, sume 100 e??roj ??iutage'}
                ]
            )
            self.create_entry(
                'sume', self.Adv, {
                    'para': 'Konsiderante ??ion'
                }, [
                    {'sent': 'Sume, li ne intencas veni'},
                    {'sent': 'Sume, unu piedbato sur la posta??on estas pli klara'}
                ]
            )
            self.create_entry(
                'mi', self.Pron, {
                    'para': 'Uzata de iu, parolanta pri si'
                }, [
                    {'sent': 'Mi amas min mem'}
                ]
            )
            self.create_entry(
                'mi', self.Pron, {
                    'para': 'La sama, uzata subst-e k signanta ies memon'
                }, [
                    {'sent': 'A animo ekrigardis la ku??ejon, kie ku??is la polvoformita??o, fremda kopio de ??ia mi'},
                    {'sent': 'La rilato de mia mi al la universo k al la eterneco'}
                ]
            )
            self.create_entry(
                'sed', self.Conj, {
                    'para': 'Montranta kontra??econ, malsamecon a?? diferencon inter tio, kio anta??as, k tio, '
                            'kio sekvas, k sekve servanta por esprimi limigan kondi??on, e?? anka?? surprizon a?? nur '
                            'simplan transiron al alia ideo'
                }, [
                    {'sent': 'Mi volis ??losi la pordon, sed mi perdis la ??losilon'},
                    {'sent': 'Lingvo arta ne sole povas, sed devas esti pli perfekta, ol lingvoj naturaj'}
                ]
            )

        def _klg_(self):
            """
            Preset Klingon

            Description from https://wikipedia.org.
            """
            self.create_lang(
                'Klingon',
                'The constructed language spoken by a fictional alien race called the Klingons, in the Star Trek '
                'universe.'
            )

        def _sda_(self):
            """
            Preset Sindarin

            Description from https://wikipedia.org.
            """
            self.create_lang(
                'Sindarin',
                'One of the constructed languages devised by J. R. R. Tolkien for use in his fantasy stories set in '
                'Arda, primarily in Middle-earth. Sindarin is one of the many languages spoken by the Elves. The word '
                'Sindarin is a Quenya word.'
            )

    def apply_preset(self, lang):
        if lang not in self._avail_presets:
            needle = lang.capitalize()
            stack = self._avail_presets.values()
            if needle in stack:
                index = list(stack).index(needle)
                lang = list(self._avail_presets.keys())[index]
            else:
                self.print_error(self.style.ERROR("ERROR: No preset named '%s'." % lang))
                self.print("Use 'makepresets -l' to show all available presets.")
                exit(1)

        name = self._avail_presets[lang]
        method = '_%s_' % lang

        if lang in self.preset_applied:
            self.print_error(self.style.ERROR("ERROR: Preset '%s' is already applied!" % name))
            self.print('Abort.')
            exit(1)

        try:
            self.print('Applying preset: %s...' % name)
            with transaction.atomic():
                self._PresetApplyingFunctions().__getattribute__(method)()
        except IntegrityError as ex:
            self.print_error(self.style.ERROR(
                'ERROR: Integrity Error. Either this preset is already applied or its application is incomplete.'
            ))
            raise ex

        self.preset_applied.append(lang)

    class _ListPresetsAction(Action):
        def __init__(self, option_strings, dest=SUPPRESS, default=SUPPRESS, presets=None, help=''):
            super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)
            self.presets = presets

        def __call__(self, parser, *args, **kwargs):
            message = 'No presets available.'
            if self.presets is not None:
                message = self.format_presets()
            parser.__getattribute__('_print_message')(message, sys.stdout)
            parser.exit()

        def format_presets(self):
            sequence = 1
            presets = ':: All available Presets:\n'
            for key in self.presets:
                name = self.presets[key]
                presets += ':: (%s) [%s] %s\n' % (sequence, key, name)
                sequence += 1
            return presets

    def add_arguments(self, parser):
        parser.register('action', 'list_presets', self._ListPresetsAction)
        parser.add_argument(
            'presets', nargs='+',
            help='Specify target language preset(s). Use either fullname or abbreviation.'
        )
        parser.add_argument(
            '-l', '--list', action='list_presets', presets=self._avail_presets,
            help='List all available presets.'
        )

    def handle(self, *args, **options):
        try:
            for lang in options['presets']:
                self.apply_preset(lang)

            if len(self.preset_applied) == 0:
                self.print('No presets applied.')
                exit(0)

            self.print(self.style.SUCCESS('All Preset(s) applied.'))
        except DatabaseError as ex:
            self.print_error(self.style.ERROR('Failed applying preset.'))
            if options['traceback']:
                raise ex
        except KeyboardInterrupt:
            self.print('\nOperation cancelled.')
