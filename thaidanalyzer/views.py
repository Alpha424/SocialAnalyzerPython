from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseRedirect
from django.shortcuts import render

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


    return render(request, 'start.html', {'error' : None})