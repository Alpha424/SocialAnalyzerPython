import csv

def ParseCSVFile(file):
    data = [row for row in csv.reader(file.read().decode('utf-8').splitlines())]
    return data

def ParseXLSFile(file):
    #TODO: XLS file parse
    pass