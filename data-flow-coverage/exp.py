from enum import Enum
import re


class Position:
    line: int
    char: int

    def __init__(self, position):
        locations = position.split(':')
        self.line = int(locations[0])
        self.char = int(locations[1])

    def __str__(self):
        return str(self.line) + '-' + str(self.char)

    def __eq__(self, other):
        return True if other.line == self.line and other.char == self.char else False

    def __le__(self, other):
        if self == other:
            return True
        else:
            return self < other

    def __lt__(self, other):
        if self.line < other.line:
            return True
        elif self.line == other.line and self.char < other.char:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.line > other.line:
            return True
        elif self.line == other.line and self.char > other.char:
            return True
        else:
            return False

    def __ge__(self, other):
        if self == other:
            return True
        else:
            return self > other


class ExpType(Enum):
    condition = 1
    guard = 2
    expression = 3
    function_def = 4


class Exp:
    begin: Position
    end: Position
    children: []
    text: str
    function_name: str
    exp_type: ExpType
    father: None

    def __init__(self, string):
        content = string.strip(",(").split(',')
        positions = content[0].split('-')
        self.begin = Position(positions[0])
        self.end = Position(positions[1])
        self.children = []
        self.text = ''
        self.function_name = ''
        description = content[1]
        if 'CondBinBox' in description:
            self.exp_type = ExpType.condition
        elif 'GuardBinBox' in description:
            self.exp_type = ExpType.guard
        elif 'TopLevelBox' in description:
            self.exp_type = ExpType.function_def
            self.function_name = re.findall(r'"([^"]*)"', description)[0]
        else:
            self.exp_type = ExpType.expression

    def __str__(self):
        return self.text + ' \nposition  ' + self.begin.__str__() + ' till ' + self.end.__str__() + '\ntype ' \
               + self.exp_type.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.begin == other.begin and self.end == other.end:
            return True
        else:
            return False

    def add_child(self, exp):
        exp.father = self
        self.children.append(exp)

    def set_text(self, text):
        self.text = text

    def contains(self, exp):
        if self.begin <= exp.begin and exp.end <= self.end:
            return True
        else:
            return False

    def next_child(self, exp):
        self.children.sort(key=lambda x: x.begin)
        index = self.children.index(exp)
        if index == len(self.children):
            return None
        else:
            return self.children[index + 1]
