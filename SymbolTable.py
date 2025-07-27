class SymbolTableEntry:
    def __init__(self, name, lexeme, value=None, type=None):
        self.name = name
        self.lexeme = lexeme
        self.value = value
        self.type = type

    def __str__(self):
        return f"({self.name}, {self.lexeme}, {self.value}, {self.type})"
