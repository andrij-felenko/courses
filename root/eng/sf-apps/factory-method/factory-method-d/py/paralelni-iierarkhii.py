from abc import ABC, abstractmethod

class Figure(ABC):
    # фабричний метод — ШОВ між ієрархією фігур та ієрархією маніпуляторів
    @abstractmethod
    def create_manipulator(self) -> "Manipulator": ...
    @abstractmethod
    def draw(self) -> None: ...

class LineFigure(Figure):
    def create_manipulator(self) -> "Manipulator":
        return LineManipulator(self)
    def draw(self) -> None: ...

class TextFigure(Figure):
    def create_manipulator(self) -> "Manipulator":
        return TextManipulator(self)
    def draw(self) -> None: ...
