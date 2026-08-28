from abc import ABC, abstractmethod

class Component(ABC):
    def __init__(self):
        self.parent: "Composite | None" = None   # зворотне посилання вгору

    @abstractmethod
    def size(self) -> int: ...

class Leaf(Component):
    def __init__(self, num_bytes: int):
        super().__init__()
        self._bytes = num_bytes
    def size(self) -> int:
        return self._bytes

class Composite(Component):
    def __init__(self):
        super().__init__()
        self.children: list[Component] = []

    def add(self, child: Component) -> None:
        if child.parent is not None:
            child.parent.remove(child)            # від'єднати від старого батька
        self.children.append(child)               # 1) зв'язок униз
        child.parent = self                        # 2) зв'язок угору

    def remove(self, child: Component) -> None:
        self.children.remove(child)
        child.parent = None

    def size(self) -> int:
        return sum(c.size() for c in self.children)
