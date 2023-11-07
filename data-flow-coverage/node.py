from enum import Enum
from exp import Exp


class NodeType(Enum):
    function_def = 1
    expression = 2


class Node:
    exp: Exp
    function_name: str
    next: []
    node_type: NodeType
    call: None
    tags: []

    def __init__(self, exp, nodes, node_type=NodeType.expression, function_name='', tags=[]):
        self.exp = exp
        self.next = nodes
        self.node_type = node_type
        self.function_name = function_name
        self.call = None
        self.tags = tags

    def __str__(self):
        if self.node_type == NodeType.function_def:
            return self.function_name
        else:
            return self.exp.__str__() + ' \n tags ' + str(self.tags)

    def __repr__(self):
        return self.__str__()

