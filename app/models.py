import inspect

from django.db import models


class Application(models.Model):
    name = models.CharField(max_length=256)


class ObjectTag(models.Model):
    model = models.CharField(max_length=100)
    name = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        if inspect.isclass(self.model):
            self.model = self.model.__name__
        super().save(*args, **kwargs)

    def __str__(self):
        return '(%s) %s' % (self.model, self.name)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['model', 'name'], name='unique_model_tag')
        ]


class Font(models.Model):
    name = models.CharField(max_length=256, unique=True)
    file = models.FilePathField()


class GlyphSet(models.Model):
    name = models.CharField(max_length=256, unique=True)
    vertical = models.BooleanField(default=False)
    upward = models.BooleanField(default=False)
    right_to_left = models.BooleanField(default=False)
    description = models.TextField(blank=True)


class Glyph(models.Model):
    glyph_set = models.ForeignKey(GlyphSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)


class Language(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(ObjectTag)

    def __str__(self):
        return self.name


class Orthography(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    font = models.ForeignKey(Font, on_delete=models.CASCADE)


class WordClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbr = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = 'Word classes'

    def __str__(self):
        return self.name


class Word(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='words')
    transcript = models.CharField(max_length=256)
    unicode = models.CharField(blank=True, max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['language', 'transcript'], name='unique_language_word')
        ]

    def __str__(self):
        return self.transcript


class Accent(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    ipa = models.CharField(max_length=256)


class InflectionClass(models.Model):
    range = models.ManyToManyField(WordClass)
    name = models.CharField(max_length=50)
    note = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = 'Inflection classes'

    def __str__(self):
        return self.name


class InflectionTag(models.Model):
    clss = models.ForeignKey(InflectionClass, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    note = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Inflection(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    tags = models.ManyToManyField(InflectionTag)
    transcript = models.CharField(max_length=256)
    unicode = models.CharField(blank=True, max_length=256)

    def __str__(self):
        return self.transcript


class Entry(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='entries')
    word_class = models.ForeignKey(WordClass, on_delete=models.CASCADE)
    tags = models.ManyToManyField(ObjectTag)
    paraphrase = models.CharField(max_length=256)
    note = models.CharField(blank=True, max_length=256)

    class Meta:
        verbose_name_plural = 'Entries'


class ExampleSentence(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='examples')
    transcript = models.CharField(max_length=500)
    unicode = models.CharField(blank=True, max_length=500)
    note = models.CharField(blank=True, max_length=500)

