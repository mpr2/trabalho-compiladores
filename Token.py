from enum import Enum

class Token:
    def __init__(self, pos, name, attr=None):
        self.pos = pos
        self.name = name
        self.attr = attr

    def __str__(self):
        return f"({self.name}, {self.attr}, pos={self.pos})"

class TokenName(Enum):
    RELOP = 1
    IGNORE = 2
    EOF = 3

    def __str__(self):
        return self.name


class TokenAttr(Enum):
    LE = 1
    NE = 2
    LT = 3
    EQ = 4
    GE = 5
    GT = 6

    def __str__(self):
        return self.name
