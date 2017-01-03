from django.http import HttpResponseRedirect
from django.shortcuts import render
import csv
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
        data = [row for row in csv.reader(uploadedFile.read().decode('utf-8').splitlines())]
        if data is None or len(data) == 0:
            return render(request, 'start.html', {'error': 'Входной файл пуст'})
        columns = len(data[0])
        for row in data:
            if len(row) != columns:
                return render(request, 'start.html', {'error': 'Входной файл имеет неправильную структуру'})
        request.session['data'] = data
        return HttpResponseRedirect('/enterattributes')
    return render(request, 'start.html', {'error' : None})


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
                                                                    'error' : 'Необходимо заполнить все поля'
                                                                    })
                attributes.append(a)
            if len(attributes) != len(set(attributes)):
                return render(request, 'enterattributes.html', {'firstrowvalues': data[0],
                                                                'usefirstrowvalues': usefirstrowvalues,
                                                                'error': 'Имена признаков не могут повторяться'
                                                                })
            dictSet = []
            startIndex = 1 if usefirstrowvalues else 0
            for i in range(startIndex, len(data)):
                dict = {}
                for j in range(len(attributes)):
                    dict[attributes[j]] = data[i][j]
                dictSet.append(dict)
            request.session['dictset'] = dictSet
            request.session['rows'] = len(dictSet)
            request.session['columns'] = len(dictSet[0])
            request.session['attributes'] = attributes
            return HttpResponseRedirect('/selectkeyattribute/')
    return render(request, 'enterattributes.html', {'firstrowvalues' : data[0], 'usefirstrowvalues' : usefirstrowvalues})


def selectkeyattribute(request):
    if request.session.get('data') is None:
        return HttpResponseRedirect('/start/')
    if request.session.get('dictset') is None:
        return HttpResponseRedirect('/enterattributes/')
    if request.POST and request.POST.get('sb') == 'proceed':
        selectedAttribute = request.POST['keyattribute']
        request.session['keyattribute'] = selectedAttribute
    attributes = request.session['attributes']
    return render(request, 'selectkeyattribute.html', {'attributes' : attributes})