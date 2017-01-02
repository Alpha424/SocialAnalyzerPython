from django.contrib.sessions.models import Session
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseRedirect
from django.shortcuts import render
from thaidanalyzer.utils.files import *
# Create your views here.
def default_page(request):
    return HttpResponseRedirect('/start/')
def start(request):
    if request.POST and request.FILES.get('datafile') is not None:
        uploadedFile = request.FILES['datafile']
        extension = ''
        if uploadedFile.name.endswith('csv'):
            extension = 'csv'
        elif uploadedFile.name.endswith('xls') or uploadedFile.name.endswith('xlsx'):
            extension = 'xls'
        else:
            return render(request, 'start.html', {'error' : 'Входной файл имел неправильный формат'})
        request.session['dictset'] = CSVToDictionarySet(uploadedFile)

    return render(request, 'start.html', {'error' : None})