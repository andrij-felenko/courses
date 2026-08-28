from typing import Protocol

# Чесний мінімум: тільки читання.
class ReadableList(Protocol):
    def get(self, i: int): ...
    def size(self) -> int: ...

# Розширення: додавання — окрема обіцянка.
class MutableList(ReadableList, Protocol):
    def add(self, x) -> None: ...

# Змінний список має ВСІ методи — отже структурно він MutableList.
class ArrayList:
    def __init__(self):
        self._items = []
    def get(self, i):        return self._items[i]
    def size(self) -> int:   return len(self._items)
    def add(self, x) -> None:
        self._items.append(x)

# Незмінний НЕ має add — отже структурно він лише ReadableList.
class ImmutableList:
    def __init__(self, initial):
        self._items = tuple(initial)      # кортеж: сам не мутує
    def get(self, i):        return self._items[i]
    def size(self) -> int:   return len(self._items)
