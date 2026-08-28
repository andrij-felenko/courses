from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def size(self) -> int: ...

    # прозорість: методи є в кожного, але за замовчуванням чесно відмовляють
    def add(self, c: "Component") -> None:
        raise TypeError("листок не може мати дітей")

    def remove(self, c: "Component") -> None:
        raise TypeError("листок не може мати дітей")

class File(Component):
    def __init__(self, num_bytes: int):
        self._bytes = num_bytes
    def size(self) -> int:
        return self._bytes
    # add/remove успадковані — кинуть виняток, і це чесно

class Folder(Component):
    def __init__(self):
        self._children: list[Component] = []
    def size(self) -> int:
        return sum(c.size() for c in self._children)
    def add(self, c: Component) -> None:        # перевизначає
        self._children.append(c)
    def remove(self, c: Component) -> None:
        self._children.remove(c)
