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

def GetSplitRate(dictArray, attribute, keyAttribute, split):
    selectionA = FilterDictArrayByAttributeValues(dictArray, attribute, split[0])
    selectionB = FilterDictArrayByAttributeValues(dictArray, attribute, split[1])
    n1 = len(selectionA)
    n2 = len(selectionB)
    p1 = GetModalRateForAttribute(selectionA, keyAttribute)
    p2 = GetModalRateForAttribute(selectionB, keyAttribute)
    rate = n1 * p1 + n2 * p2
    return rate

def GetBestSplitDecision(dictArray, attribute, keyAttribute):
    possibleSplits = GetPossibleSplitsForAttribute(dictArray, attribute)
    maxSplitRate = -1
    bestSplit = None
    for split in possibleSplits:
        rate = GetSplitRate(dictArray, attribute, keyAttribute, split)
        if rate > maxSplitRate:
            maxSplitRate = rate
            bestSplit = split
    return bestSplit

class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

def THAID(dictArray, attributeList, keyAttribute):
    if dictArray == None or attributeList == None or keyAttribute == None:
        return
    if len(attributeList) == 0:
        return
    attributes = list(attributeList)
    if keyAttribute in attributes:
        attributes.remove(keyAttribute)
    node = Node(None)
    BuildTree(dictArray, attributes, keyAttribute, node)
    return

def BuildTree(dictArray, attributeList, keyAttribute, treenode, modalRateStop = 0.9):
    if len(dictArray) == 0 or len(attributeList) == 0:
        return
    if GetModalRateForAttribute(dictArray, keyAttribute) >= modalRateStop:
        return
    attributes = list(attributeList)
    bestAttribute = attributes[0]
    bestAttributeSplitRate = -1
    bestAttributeSplit = None
    for a in attributes:
        attributeBestSplit = GetBestSplitDecision(dictArray, a, keyAttribute)
        attributeBestSplitRate = GetSplitRate(dictArray, a, keyAttribute, attributeBestSplit)
        if(attributeBestSplitRate > bestAttributeSplitRate):
            bestAttribute = a
            bestAttributeSplitRate = attributeBestSplitRate
            bestAttributeSplit = attributeBestSplit
    treenode.add_child(Node((bestAttribute, bestAttributeSplit[0])))
    treenode.add_child(Node((bestAttribute, bestAttributeSplit[1])))
    attributes.remove(bestAttribute)
    BuildTree(FilterDictArrayByAttributeValues(dictArray, bestAttribute, bestAttributeSplit[0]), attributes, keyAttribute, treenode.children[0])
    BuildTree(FilterDictArrayByAttributeValues(dictArray, bestAttribute, bestAttributeSplit[1]), attributes, keyAttribute, treenode.children[1])
