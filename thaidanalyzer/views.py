import json
import itertools
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
            return HttpResponseRedirect('/excludefeatures/')
        else:
            form.add_error(None, 'Имена признаков не могут повторяться')
    return render(request, 'enterattributes.html', {'form' : form})

def excludeFeatures(request):
    if not (request.session.get('dictArray') or request.session.get('attributes')):
        return HttpResponseRedirect('/start/')
    attributes = request.session.get('attributes')
    form = ExcludeFeaturesForm(request.POST or None, attrs=attributes)
    if form.is_valid():
        to_exclude = []
        for key, val in form.cleaned_data.items():
            if val:
                to_exclude.append(key)
        if len(attributes) - len(to_exclude) < 2:
            form.add_error(None, 'Для работы алгоритма требуется как минимум 2 признака')
            return render(request, 'excludefeatures.html', {'form': form})
        request.session['attributes'] = list(itertools.filterfalse(lambda e: e in to_exclude, attributes))
        return HttpResponseRedirect('/selectkeyattribute/')
    return render(request, 'excludefeatures.html', {'form' : form})

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
            return HttpResponseRedirect('/selectmethod/')
        except Exception as e:
            form.add_error(None, str(e))
    return render(request, 'selectkeyattribute.html', {'form': form})

def selectmethod(request):
    if not(request.session.get('dictArray')
           or request.session.get('attributes')
           or request.get('keyattribute')):
        return HttpResponseRedirect('/start/')
    form = MethodSelectionForm(request.POST or None)
    if form.is_valid() and form.cleaned_data.get('method'):
        try:
            request.session['method'] = form.cleaned_data.get('method')
            return HttpResponseRedirect('/report/')
        except Exception as e:
            form.add_error(None, str(e))
    return render(request, 'selectmethod.html', {'form' : form})
def report(request):
    if not (request.session.get('dictArray')
            or request.session.get('attributes')
            or request.session.get('keyattribute')
            or request.session.get('method')):
        return HttpResponseRedirect('/start/')
    dictArray = request.session.get('dictArray')
    attributes = request.session.get('attributes')
    keyattribute = request.session.get('keyattribute')
    method = request.session.get('method')
    TreeBuilder = None
    if method == 'THAID':
        TreeBuilder = THAIDTreeBuilder(dictArray, attributes, keyattribute)
    else:
        TreeBuilder = ExternalCHAIDTreeBuilder(dictArray, attributes, keyattribute)
    treeHead = TreeBuilder.BuildTree()
    context = {}
    context['series_len'] = len(dictArray)
    context['features_num'] = len(attributes)
    context['groups_num'] = GetTreeLeavesNumber(treeHead)
    context['method'] = method
    distribution_chart = {
        'chart': {
            'plotBackgroundColor': 'white',
            'type': 'pie'
        },
        'title': {
            'text': 'Распределение ключевого признака в выборке'
        },
        'tooltip': {
            'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        'plotOptions': {
            'pie': {
                'allowPointSelect': 'true',
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': 'true',
                    'format': '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        'series': [{
            'name': 'Доля признака',
            'colorByPoint': 'true',
            'data': [{'name': key, 'y': val} for key, val in EvaluateDistribution(dictArray, keyattribute).items()]
        }]
    }
    groups_charts = []
    groups = GetTreeLeaves(treeHead)
    c = 1
    for group in groups:
        slice = FilterSetByTreePath(dictArray, group)
        dist_in_group = EvaluateDistribution(slice, keyattribute, percentage=False)
        chart = {
            'chart' : {
                'type' : 'column'
            },
            'plotOptions': {
                'column' : {
                    'dataLabels' : {
                        'enabled' : 'true'
                    }
                }
            },
            'title' : {
                'text' : 'Распределение ключевого признака в группе %d' % c
            },
            'subtitle' : {
                'text' : ' | '.join(GetTreePathAsList(group))
            },
            'xAxis' : {
                'categories' : list(dist_in_group.keys())
            },
            'yAxis' : {
                'title' : 'Кол-во наблюдений'
            },
            'series' : [{
                'data' : list(dist_in_group.values()),
                'name' : 'Группа %d' % c
            }]
        }
        c += 1
        groups_charts.append(json.dumps(chart, ensure_ascii=False))

    context['distribution_chart'] = json.dumps(distribution_chart, ensure_ascii=False)
    context['groups_charts'] = groups_charts
    dotTree = RenderTree(treeHead, dictArray)
    context['tree'] = dotTree.pipe(format='svg')
    return render(request, 'report.html', context)