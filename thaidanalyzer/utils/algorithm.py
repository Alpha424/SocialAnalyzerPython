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
    def sorted_k_partitions(seq, k):
        n = len(seq)
        groups = []

        def generate_partitions(i):
            if i >= n:
                yield list(map(tuple, groups))
            else:
                if n - i > k - len(groups):
                    for group in groups:
                        group.append(seq[i])
                        yield from generate_partitions(i + 1)
                        group.pop()

                if len(groups) < k:
                    groups.append([seq[i]])
                    yield from generate_partitions(i + 1)
                    groups.pop()

        result = generate_partitions(0)
        return result

    possibleValues = list(GetPossibleValuesForAttribute(dictArray, attribute))
    if not possibleValues or len(possibleValues) == 1:
        return None
    splits = sorted_k_partitions(possibleValues, 2)
    return list(splits)

def GetSplitRate(dictArray, attribute, keyAttribute, split):
    assert len(split) >= 2
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
    if possibleSplits is None:
        return None
    if len(possibleSplits) == 1:
        return possibleSplits[0]
    maxSplitRate = -1
    bestSplit = None
    for split in possibleSplits:
        rate = GetSplitRate(dictArray, attribute, keyAttribute, split)
        if rate > maxSplitRate:
            maxSplitRate = rate
            bestSplit = split
    return bestSplit

class Node(object):
    counter = 0
    def __init__(self, data):
        self.data = data
        self.children = None
        self.id = Node.counter
        Node.counter += 1

    def add_child(self, obj):
        if self.children is None:
            self.children = []
        self.children.append(obj)

def THAID(dictArray, attributeList, keyAttribute):
    if dictArray is None:
        raise Exception('Null set')
    if attributeList is None:
        raise Exception('No attributes given')
    if keyAttribute is None:
        raise Exception('No key attribute given')
    if len(attributeList) == 0:
        return
    attributes = list(attributeList)
    if keyAttribute in attributes:
        attributes.remove(keyAttribute)
    treeRoot = Node(None)
    BuildTree(dictArray, attributes, keyAttribute, treeRoot)
    return treeRoot

def BuildTree(dictArray, attributeList, keyAttribute, treenode, modalRateStop = 0.9):
    if len(dictArray) == 0:
        return
    if GetModalRateForAttribute(dictArray, keyAttribute) >= modalRateStop:
        return
    attributes = list(attributeList)
    for a in attributes:
        if not GetPossibleSplitsForAttribute(dictArray, a):
            attributes.remove(a)
    if not attributes:
        return
    bestAttribute = None
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