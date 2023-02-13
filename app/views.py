from django.shortcuts import render, redirect
from watson import search as watson

from app.models import Word, Language, Entry, ExampleSentence


def index(request):

    return render(request, 'dictionary/home.html', {

    })


def search(request):
    val = request.GET.get('w', '').strip()

    if len(val) == 0:
        return redirect('index')

    words = Word.objects.filter(transcript__icontains=val)
    entries = Entry.objects.filter(paraphrase__icontains=val).exclude(word_id__in=words)
    sentences = ExampleSentence.objects.filter(transcript__icontains=val).exclude(entry__word_id__in=words)

    return render(request, 'search.html', {
        'search_value': val,
        'results': {
            'words': watson.filter(words, val),
            'entries': watson.filter(entries, val),
            'sentences': watson.filter(sentences, val)
        }
    })


def library(request):
    lang = Language.objects.all()
    return render(request, 'library.html')


def word(request, name):
    word_object = Word.objects.get(transcript=name)

    return render(request, 'dictionary/word.html', {
        'search_value': name,
        'word': word_object,
    })
