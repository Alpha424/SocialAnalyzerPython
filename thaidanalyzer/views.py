from django.http import HttpResponseRedirect
from django.shortcuts import render
from thaidanalyzer.utils.misc import *
from thaidanalyzer.utils.algorithm import *
from thaidanalyzer.forms import *
def default_page(request):
    return HttpResponseRedirect('/start/')
def start(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploadedFile = request.FILES.get('file')
            request.session['file'] = uploadedFile
            if uploadedFile.name.endswith('.csv'):
                request.session['extension'] = 'csv'
                return HttpResponseRedirect('/csvoptions/')
            elif uploadedFile.name.endswith('xls') or uploadedFile.name.endswith('xlsx'):
                request.session['extension'] = 'excel'
                return HttpResponseRedirect('/xlsoptions/')
            else:
                raise Exception('File extension exception')
    else:
        form = FileUploadForm()
    return render(request, 'start.html', {'form' : form})

def csvoptions(request):
    if request.session.get('file') is None or request.session.get('extension') != 'csv':
        return HttpResponseRedirect('/start/')
    if request.method == 'POST':
        form = CSVOptionsForm(request.POST)
        if form.is_valid():
            try:
                separator = form.cleaned_data['separator']
                codec = form.cleaned_data['codec']
                request.session['data'] = ParseCSVFile(request.session['file'], separator, codec)
                del request.session['file']
                return HttpResponseRedirect('/enterattributes/')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = CSVOptionsForm()
    return render(request, 'csvoptions.html', {'form' : form})

def xlsoptions(request):
    if request.session.get('file') is None or request.session.get('extension') != 'excel':
        return HttpResponseRedirect('/start/')
    try:
        sheets = ExtractSheetsFromXLSFile(request.session.get('file'))
    except:
        return HttpResponseRedirect('/start/')
    if len(sheets) == 0:
        return HttpResponseRedirect('/start/')
    form = XLSOptionsForm(request.POST or None, sheets=sheets)
    if form.is_valid():
        sheet_idx = int(form.cleaned_data['sheet_selection'])
        try:
            request.session['data'] = ParseXLSFile(sheets[sheet_idx])
            del request.session['file']
            return HttpResponseRedirect('/enterattributes/')
        except Exception as e:
            form.add_error(None, str(e))
    return render(request, 'xlsoptions.html', {'form' : form})

def enterattributes(request):
    if request.session.get('data') is None or len(request.session.get('data')) == 0:
        return HttpResponseRedirect('/start/')
    if 'dictArray' in request.session:
        del request.session['dictArray']
    if 'attributes' in request.session:
        del request.session['attributes']
    data = request.session.get('data')
    columnsNum = len(data[0])
    form = EnterAttributesForm(request.POST or None, narg=columnsNum)
    if request.method == 'POST':
        attributes = []
        usefirstrowvalues = 'form_usefirstrowvalues' in request.POST
        if usefirstrowvalues:
            attributes = data[0]
        else:
            attributes = [form.data.get('arg%s' % i) for i in range(columnsNum)]
        for a in attributes:
            if not str(a).strip():
                form.add_error(None, 'Не все поля заполнены')
                return render(request, 'enterattributes.html', {'form': form})
        if len(attributes) == len(set(attributes)):
            dictArray = ConvertRawDataToDictArray(data, attributes, usefirstrowvalues)
            request.session['dictArray'] = dictArray
            request.session['attributes'] = attributes
            del request.session['data']
            return HttpResponseRedirect('/selectkeyattribute/')
        else:
            form.add_error(None, 'Имена признаков не могут повторяться')
    return render(request, 'enterattributes.html', {'form' : form})

def selectkeyattribute(request):
    if not(request.session.get('dictArray') or request.session.get('attributes')):
        return HttpResponseRedirect('/start/')
    attributes = request.session['attributes']
    form = SelectKeyAttributeForm(request.POST or None, attributes=attributes)
    if len(attributes) < 2:
        form.add_error(None, 'Для работы алгоритма необходимо как минимум наличие двух признаков, включая ключевой')
        return render(request, 'selectkeyattribute.html', {'form' : form})
    if form.is_valid():
        try:
            keyAttributeIndex = int(form.cleaned_data.get('key_attribute_selection'))
            request.session['keyattribute'] = attributes[keyAttributeIndex]

        except Exception as e:
            form.add_error(None, str(e))
    return render(request, 'selectkeyattribute.html', {'form': form})