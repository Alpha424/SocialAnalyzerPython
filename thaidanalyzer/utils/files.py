import codecs
import csv
def CSVToDictionarySet(file):
    file.open()
    reader = csv.reader(codecs.EncodedFile(file, "utf-8"), delimiter=',')
    for row in reader:
        print(",".join(row))