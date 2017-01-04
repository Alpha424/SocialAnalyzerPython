import operator


class Tree:
    class Node:
        filterAttribute = None
        filterValues = []
        leftChild = None
        rightChild = None
        def __init__(self, filterAttribute, filterValues):
            self.filterAttribute = filterAttribute
            self.filterValues = filterValues
    head = None
    def __init__(self):
        self.head = Tree.Node(None, None)


def GetPossibleValuesForAttribute(dictArray, attribute):
    values = set()
    for e in dictArray:
        values.add(e[attribute])
    return values
def FilterDictArrayByAttributeValues(dictArray, attribute, possibleValues):
    res = filter(lambda d: d[attribute] in possibleValues, dictArray)
    return list(res)

def EvaluateDistribution(dictArray, keyAttribute):
    res = {}
    N = len(dictArray)
    possibleValues = GetPossibleValuesForAttribute(dictArray, keyAttribute)
    for value in possibleValues:
        res[value] = len([x for x in dictArray if x[keyAttribute] == value]) / N
    return res
def GetModalValueForAttribute(dictArray, attribute):
    dist = EvaluateDistribution(dictArray, attribute)
    return max(dist, key=dist.get)
def GetModalRateForAttribute(dictArray, attribute):
    dist = EvaluateDistribution(dictArray, attribute)
    maxKey = max(dist, key=dist.get)
    return dist[maxKey]
def GetPossibleSplitsForAttribute(dictArray, attribute):
    possibleValues = list(GetPossibleValuesForAttribute(dictArray, attribute))
    if possibleValues is None or len(possibleValues) == 0:
        return None
    if len(possibleValues) == 1:
        return possibleValues[0]
    splits = []
    for i in range(1, len(possibleValues)):
        splits.append((possibleValues[0:i], possibleValues[i:]))
    return splits
def GetBestSplitDecision(dictArray, attribute, keyAttribute):
    possibleSplits = GetPossibleSplitsForAttribute(dictArray, attribute)
    splitRates = {}
    for split in possibleSplits:
        selectionA = FilterDictArrayByAttributeValues(dictArray, attribute, split[0])
        selectionB = FilterDictArrayByAttributeValues(dictArray, attribute, split[1])
        n1 = len(selectionA)
        n2 = len(selectionB)
        p1 = GetModalRateForAttribute(selectionA, keyAttribute)
        p2 = GetModalRateForAttribute(selectionB, keyAttribute)
        rate = n1 * p1 + n2 * p2
        splitRates[split] = rate
        continue
    return splitRates



class THAIDAnalyzer:
    dictArray = []
    keyAttribute = None
    tree = None
    def __init__(self, dictArray, keyAttribute):
        self.dictArray = dictArray
        self.keyAttribute = keyAttribute
        self.tree = Tree()
    def SplitSet(self, dictArr = dictArray, level = 1):
        pass


