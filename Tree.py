class Tree:
    def __init__(self, value):
        self.value = value
        self.children = []
    
    def add_child(self, tree):
        if tree is not None:
            self.children.append(tree)

    def is_leaf(self):
        return len(self.children) == 0

    def pretty_print(self, indent='', last=True):
        connector = '└── ' if last else '├── '
        print(indent + connector + str(self.value))
        indent += '    ' if last else '│   '
        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            child.pretty_print(indent, is_last)
