import json
import requests

def GetPossibleValuesForAttribute(dictArray, attribute):
    values = set()
    for e in dictArray:
        values.add(e[attribute])
    return values
def FilterDictArrayByAttributeValues(dictArray, attribute, possibleValues):
    res = filter(lambda d: d[attribute] in possibleValues, dictArray)
    return list(res)

def EvaluateDistribution(dictArray, keyAttribute, percentage = True):
    res = {}
    N = len(dictArray)
    possibleValues = GetPossibleValuesForAttribute(dictArray, keyAttribute)
    for value in possibleValues:
        res[value] = len([x for x in dictArray if x[keyAttribute] == value])
        if percentage:
            res[value] /= N
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
    rate = 0
    for s in split:
        selection = FilterDictArrayByAttributeValues(dictArray, attribute, s)
        n = len(selection)
        p = GetModalRateForAttribute(selection, keyAttribute)
        rate += n * p
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

def FilterSetByTreePath(dictArray, treeLeaf):
    filtered_array = list(dictArray)
    filters = []
    def get_filter_path_from_node(node):
        if not node.data:
            return
        filters.append(node.data)
        if node.parent:
            get_filter_path_from_node(node.parent)
    get_filter_path_from_node(treeLeaf)
    for f in filters:
        filtered_array = list(filter(lambda e: e[f[0]] in f[1], filtered_array))
    return filtered_array


class Node(object):
    counter = 0
    def __init__(self, data):
        self.data = data
        self.children = None
        self.parent = None
        self.id = Node.counter
        Node.counter += 1

    def add_child(self, obj):
        if self.children is None:
            self.children = []
        obj.parent = self
        self.children.append(obj)

class AbstractTreeBuilder(object):
    def __init__(self, dataset, attributes, keyAttribute):
        self.dataset = dataset
        self.attributes = attributes
        self.keyAttribute = keyAttribute

    def BuildTree(self):
        if not self.dataset:
            raise Exception("Empty data set")
        if not self.attributes:
            raise Exception("No attributes given")
        if not self.keyAttribute:
            raise Exception('No key attribute given')



class THAIDTreeBuilder(AbstractTreeBuilder):
    @staticmethod
    def Build_Recursive(dictArray, attributeList, keyAttribute, treenode, modalRateStop=0.9):
        if not dictArray:
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
            if (attributeBestSplitRate > bestAttributeSplitRate):
                bestAttribute = a
                bestAttributeSplitRate = attributeBestSplitRate
                bestAttributeSplit = attributeBestSplit
        treenode.add_child(Node((bestAttribute, bestAttributeSplit[0])))
        treenode.add_child(Node((bestAttribute, bestAttributeSplit[1])))
        attributes.remove(bestAttribute)
        slices = (FilterDictArrayByAttributeValues(dictArray, bestAttribute, split_part) for split_part in
                  bestAttributeSplit)
        for idx, slice in enumerate(slices):
            THAIDTreeBuilder.Build_Recursive(slice, attributes, keyAttribute, treenode.children[idx])
    def BuildTree(self):
        AbstractTreeBuilder.BuildTree(self)
        if self.keyAttribute in self.attributes:
            self.attributes.remove(self.keyAttribute)
        treeRoot = Node(None)
        THAIDTreeBuilder.Build_Recursive(self.dataset, self.attributes, self.keyAttribute, treeRoot)
        return treeRoot

class ExternalCHAIDTreeBuilder(AbstractTreeBuilder):
    @staticmethod
    def RestoreTreeFromRawDict(dict):
        def build_tree(node, d):
            feature = d.get('feature')
            values = d.get('values')
            if feature and values:
                node.data = (feature, values)
            for ch in ['child1', 'child2']:
                if d.get(ch):
                    newChild = Node(None)
                    node.add_child(newChild)
                    build_tree(newChild, d.get(ch))
        root = Node(None)
        build_tree(root, dict)
        return root
    def ExcludeRedundantFeaturesFromSet(self):
        cleaned_set = []
        for d in self.dataset:
            nd = {}
            for k, v in d.items():
                if k in self.attributes:
                    nd[k] = v
            cleaned_set.append(nd)
        self.dataset = cleaned_set

    def BuildTree(self):
        self.ExcludeRedundantFeaturesFromSet()
        data = {'dataset' : self.dataset, 'key_attribute' : self.keyAttribute}
        encoded_data = json.dumps(data, ensure_ascii=False)
        encoded_data = "'" + str(encoded_data) + "'"
        headers = {'User-Agent' : 'SocialAnalyzer',
                   'Content-Type': 'application/json; charset=utf-8',
                   }
        response = requests.post('http://webapplication120170514044253.azurewebsites.net/api/Default1',
                                 data=encoded_data.encode('utf-8'),
                                 headers=headers
                                 )
        if not response.ok:
            raise Exception("External system error")
        raw_dict = json.loads(response.json(), encoding=response.encoding)
        return ExternalCHAIDTreeBuilder.RestoreTreeFromRawDict(raw_dict)


def GetTreeLeaves(tree_head):
    if not tree_head:
        return None
    def go_deep(curr_node, leaves):
        if not curr_node.children:
            leaves.append(curr_node)
            return
        for child in curr_node.children:
            go_deep(child, leaves)
    leaves = []
    go_deep(tree_head, leaves)
    return leaves

def GetTreeLeavesNumber(tree_head):
    if not tree_head:
        return 0
    c = 0
    if not tree_head.children:
        return 1
    for child in tree_head.children:
        c += GetTreeLeavesNumber(child)
    return c

def GetTreePathAsList(node, start_at_head = True):
    def go_up(node):
        if not node.data:
            return
        path.append("%s : %s" % (str(node.data[0]), ', '.join([str(x) for x in node.data[1]])))
        if node.parent:
            go_up(node.parent)
    if not node:
        return None
    path = []
    go_up(node)
    if start_at_head:
        path.reverse()
    return path