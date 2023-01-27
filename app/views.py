from django.shortcuts import render, redirect
from .models import Language


def index(request):
    return render(request, 'index.html')


def search(request):
    val = request.GET.get('w')

    if isinstance(val, str):

        trim = val.strip()

        if len(trim) > 0:

            return render(request, 'search.html', {
                'search_value': trim
            })

    return redirect('index')


def library(request):
    lang = Language.objects.all()
    return render(request, 'library.html')
