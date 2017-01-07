from django.http import HttpResponseRedirect
from django.shortcuts import render
from thaidanalyzer.utils.misc import *
from thaidanalyzer.utils.algorithm import *
def default_page(request):
    return HttpResponseRedirect('/start/')
def start(request):
    if request.POST and request.FILES.get('datafile') is not None:
        uploadedFile = request.FILES['datafile']
        request.session['file'] = uploadedFile
        if uploadedFile.name.endswith('csv'):
            request.session['extension'] = 'csv'
            return HttpResponseRedirect('/csvoptions/')
        elif uploadedFile.name.endswith('xls') or uploadedFile.name.endswith('xlsx'):
            request.session['extension'] = 'excel'
            return HttpResponseRedirect('/xlsoptions/')
        else:
            return render(request, 'start.html', {'error' : 'Входной файл имел неправильный формат'})
    return render(request, 'start.html', {'error' : None})

def csvoptions(request):
    if request.session.get('file') is None or request.session.get('extension') != 'csv':
        return HttpResponseRedirect('/start/')
    if request.POST and request.POST.get('separator') is not None and request.POST.get('codec') is not None:
        try:
            request.session['data'] = ParseCSVFile(request.session['file'], request.POST.get('separator'), request.POST.get('codec'))
            del request.session['file']
            return HttpResponseRedirect('/enterattributes/')
        except Exception as e:
            return render(request, 'csvoptions.html', {'error' : e})
    return render(request, 'csvoptions.html', {})

def xlsoptions(request):
    if request.session.get('file') is None or request.session.get('extension') != 'excel':
        return HttpResponseRedirect('/start/')
    file = request.session.get('file')
    book = xlrd.open_workbook(file_contents=file.read())
    sheets = book.sheet_names()
    if len(sheets) == 0:
        return HttpResponseRedirect('/start/')
    if request.POST and request.POST.get('sheet') is not None and book is not None:
        try:
            sheet_idx = int(request.POST.get('sheet'))
            request.session['data'] = ParseXLSFile(book.sheet_by_index(sheet_idx))
            del request.session['file']
            return HttpResponseRedirect('/enterattributes/')
        except Exception as e:
            return render(request, 'xlsoptions.html', {'sheets': sheets, 'error' : e})

    return render(request, 'xlsoptions.html', {'sheets' : sheets})

def enterattributes(request):
    if request.session.get('data') is None:
        return HttpResponseRedirect('/start/')
    usefirstrowvalues = False
    data = request.session['data']
    columnsNum = len(data[0])
    if request.POST and request.POST.get('checkbox') is not None:
        usefirstrowvalues = request.POST.get('checkbox') == 'usefirstrowvalues'
    if request.POST and request.POST.get('sb') is not None:
        if request.POST['sb'] == 'proceed':
            attributes = []
            for i in range(columnsNum):
                a = request.POST['attribute' + str(i)].strip()
                if len(a) == 0:
                    return render(request, 'enterattributes.html', {'firstrowvalues' : data[0],
                                                                    'usefirstrowvalues' : usefirstrowvalues,
                                                                    'error' : 'Необходимо заполнить все поля'})
                attributes.append(a)
            if len(attributes) != len(set(attributes)):
                return render(request, 'enterattributes.html', {'firstrowvalues': data[0],
                                                                'usefirstrowvalues': usefirstrowvalues,
                                                                'error': 'Имена признаков не могут повторяться'})
            dictArray = ConvertRawDataToDictArray(data, attributes, usefirstrowvalues)
            request.session['dictArray'] = dictArray
            request.session['attributes'] = attributes
            del request.session['data']
            return HttpResponseRedirect('/selectkeyattribute/')
    return render(request, 'enterattributes.html', {'firstrowvalues' : data[0], 'usefirstrowvalues' : usefirstrowvalues})


def selectkeyattribute(request):
    if request.session.get('data') is None and request.session.get('dictArray') is None:
        return HttpResponseRedirect('/start/')
    attributes = request.session['attributes']
    if request.POST and request.POST.get('sb') == 'proceed':
        selectedAttribute = request.POST['keyattribute']
        request.session['keyattribute'] = selectedAttribute
        THAID(request.session['dictArray'], attributes, selectedAttribute)
    return render(request, 'selectkeyattribute.html', {'attributes' : attributes})