from abc import ABC, abstractmethod

class Expr(ABC):
    @abstractmethod
    def accept(self, v): ...          # уся обв'язка — цей один метод

class ExprVisitor(ABC):               # по методу на КОЖЕН вид вузла
    @abstractmethod
    def visit_num(self, e): ...
    @abstractmethod
    def visit_var(self, e): ...
    @abstractmethod
    def visit_neg(self, e): ...
    @abstractmethod
    def visit_add(self, e): ...
    @abstractmethod
    def visit_mul(self, e): ...

class Num(Expr):
    def __init__(self, value): self.value = value
    def accept(self, v): return v.visit_num(self)      # я — число
class Var(Expr):
    def __init__(self, name): self.name = name
    def accept(self, v): return v.visit_var(self)
class Neg(Expr):
    def __init__(self, arg): self.arg = arg
    def accept(self, v): return v.visit_neg(self)
class Add(Expr):
    def __init__(self, left, right): self.left, self.right = left, right
    def accept(self, v): return v.visit_add(self)
class Mul(Expr):
    def __init__(self, left, right): self.left, self.right = left, right
    def accept(self, v): return v.visit_mul(self)
