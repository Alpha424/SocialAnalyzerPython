import csv
import xlrd
import graphviz as gv
class FileEmptyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileStructureError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def ConvertRawDataToDictArray(data, attributes, usefirstrowvalues = False):
    dictArray = []
    startIndex = 1 if usefirstrowvalues else 0
    for i in range(startIndex, len(data)):
        dict = {}
        for j in range(len(attributes)):
            dict[attributes[j]] = data[i][j]
        dictArray.append(dict)
    return dictArray

def ParseCSVFile(file, separator=',', codec = 'utf8'):
    if len(file) == 0:
        raise FileEmptyError("Входной файл пуст")
    data = [row for row in csv.reader(file.read().decode(codec).splitlines(), delimiter=separator)]
    if len(data) == 0:
        raise FileEmptyError("Входной файл не содержит строк")
    colNum = len(data[0])
    for row in data:
        if len(row) != colNum:
            raise FileStructureError("Входной файл имел неправильную структуру")
    return data

def ParseXLSFile(sheet):
    data = []
    for row in sheet.get_rows():
        data.append([cell.value for cell in row])
    if len(data) == 0:
        raise FileEmptyError("Таблица не содержит строк")
    return data

def ExtractSheetsFromXLSFile(file):
    book = xlrd.open_workbook(file_contents=file.read())
    return book.sheets()

def RenderTree(tree_head):
    def traverse_tree(node, graph):
        nodeLabel = ""
        if node.data:
            nodeLabel = str(node.data[0]) + ": " + ', '.join(node.data[1])
        graph.node(str(node.id), label=nodeLabel)
        if not node.children:
            return node
        for child in node.children:
            c = traverse_tree(child, graph)
            graph.edge(str(node.id), str(c.id))
        return node

    g1 = gv.Graph(format='svg')
    traverse_tree(tree_head, g1)
    return g1