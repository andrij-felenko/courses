from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def size(self) -> int:        # спільний інтерфейс: обіцянка обом
        ...

class File(Component):
    def __init__(self, num_bytes: int):
        self._bytes = num_bytes

    def size(self) -> int:
        return self._bytes        # лист: власне число

class Folder(Component):
    def __init__(self):
        self._children: list[Component] = []

    def add(self, c: Component) -> None:   # тільки в компонувальника
        self._children.append(c)

    def size(self) -> int:
        return sum(c.size() for c in self._children)   # питаю, НЕ питаючи, хто це
