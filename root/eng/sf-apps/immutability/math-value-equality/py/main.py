class Tag:                          # те саме: рівність за вмістом, поле мінливе
    def __init__(self, name): self.name = name
    def __eq__(self, o): return isinstance(o, Tag) and o.name == self.name
    def __hash__(self): return hash(self.name)

s = set()
a = Tag("cola")
s.add(a)                            # кошик за hash("cola")
a.name = "beer"                     # мутація поля геша

a in s                              # False — той самий об'єкт «не в множині»
next(iter(s)) is a                  # True  — перебором він на місці
