from typing import Protocol

class ReadableList(Protocol):        # чесний мінімум: тільки читання
    def get(self, i: int): ...
    def size(self) -> int: ...

class MutableList(ReadableList, Protocol):
    def add(self, x) -> None: ...    # додавання — окрема, ширша обіцянка

# Тепер fill вимагає рівно те, що йому треба, — і незмінний сюди НЕ підставиш:
def fill(lst: MutableList) -> None:
    for i in range(lst.size()):
        lst.add(i)
