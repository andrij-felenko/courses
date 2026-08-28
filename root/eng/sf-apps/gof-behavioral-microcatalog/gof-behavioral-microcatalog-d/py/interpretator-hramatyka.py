from __future__ import annotations
from typing import Protocol

# Спільний інтерфейс: кожен вузол уміє обчислити сам себе
class Expr(Protocol):
    def interpret(self, env: dict[str, int]) -> int: ...

# Термінали — листя дерева: обчислюються без звертань кудись далі
class Num:
    def __init__(self, value: int): self.value = value
    def interpret(self, env: dict[str, int]) -> int:
        return self.value

class Var:
    def __init__(self, name: str): self.name = name
    def interpret(self, env: dict[str, int]) -> int:
        if self.name not in env:
            raise KeyError(f"невідома змінна {self.name}")
        return env[self.name]

# Нетермінали — тримають під-вирази й рекурсивно їх обчислюють
class Add:
    def __init__(self, left: Expr, right: Expr):
        self.left, self.right = left, right
    def interpret(self, env: dict[str, int]) -> int:
        return self.left.interpret(env) + self.right.interpret(env)

class Mul:
    def __init__(self, left: Expr, right: Expr):
        self.left, self.right = left, right
    def interpret(self, env: dict[str, int]) -> int:
        return self.left.interpret(env) * self.right.interpret(env)

# Вираз "x + 3 * 2" — зібраний як дерево об'єктів
tree: Expr = Add(Var("x"), Mul(Num(3), Num(2)))
print(tree.interpret({"x": 5}))   # 11
