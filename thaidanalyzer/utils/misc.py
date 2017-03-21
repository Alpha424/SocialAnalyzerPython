import csv
import xlrd
import graphviz as gv
from thaidanalyzer.utils.algorithm import FilterSetByTreePath

def ConvertRawDataToDictArray(data, attributes, usefirstrowvalues = False):
    dictArray = []
    startIndex = 1 if usefirstrowvalues else 0
    for i in range(startIndex, len(data)):
        dict = {}
        for j in range(len(attributes)):
            dict[attributes[j]] = data[i][j]
        dictArray.append(dict)
    return dictArray

def CheckTable(table):
    if not table:
        raise Exception("Входной файл пуст")
    rowLen = len(table[0])
    for row in table:
        if len(row) != rowLen or any(not x for x in row):
            raise Exception("Входной файл имел неправильную структуру")
        rowLen = len(row)


def ParseCSVFile(file, separator=',', codec = 'utf8'):
    data = [row for row in csv.reader(file.read().decode(codec).splitlines(), delimiter=separator)]
    CheckTable(data)
    return data

def ParseXLSFile(sheet):
    data = []
    for row in sheet.get_rows():
        data.append([cell.value for cell in row])
    CheckTable(data)
    return data

def ExtractSheetsFromXLSFile(file):
    book = xlrd.open_workbook(file_contents=file.read())
    return book.sheets()

def RenderTree(tree_head, dictArray, file_format = 'svg'):
    def lookup_down(node, graph):
        if node.data:
            nodeLabel = str(node.data[0]) + ": " + ', '.join(node.data[1])
        else:
            nodeLabel = str(len(dictArray))
        graph.node(str(node.id), label=nodeLabel)

        if not node.children:
            return node
        for child in node.children:
            c = lookup_down(child, graph)
            edgeLabel = str(len(FilterSetByTreePath(dictArray, c)))
            graph.edge(str(node.id), str(c.id), label=edgeLabel)
        return node

    g1 = gv.Graph(format=file_format)
    lookup_down(tree_head, g1)
    return g1