from django.db import models


class GlyphSet(models.Model):
    name = models.CharField(max_length=256)
    vertical = models.BooleanField(default=False)
    upward = models.BooleanField(default=False)
    rtl = models.BooleanField(default=False)
    description = models.TextField()


class Glyph(models.Model):
    glyph_set = models.ForeignKey(GlyphSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)


class Language(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()


class Orthography(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    glyph = models.ForeignKey(Glyph, on_delete=models.CASCADE)
    key = models.CharField(unique=True, max_length=256)


class WordClass(models.Model):
    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=10)


class Word(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    transcript = models.CharField(max_length=256)
    ipa = models.CharField(max_length=256)


class InflectionClass(models.Model):
    word_class = models.ForeignKey(WordClass, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    note = models.CharField(max_length=256)


class InflectionTags(models.Model):
    belongs_to = models.ForeignKey(InflectionClass, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    note = models.CharField(max_length=256)


class Inflection(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    tags = models.ManyToManyField(InflectionTags)
    transcript = models.CharField(max_length=256)


class Entry(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    word_class = models.ForeignKey(WordClass, on_delete=models.CASCADE)
    paraphrase = models.CharField(max_length=256)
    note = models.CharField(blank=True, max_length=256)


class ExampleSentence(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    value = models.CharField(max_length=500)
    note = models.CharField(blank=True, max_length=500)
