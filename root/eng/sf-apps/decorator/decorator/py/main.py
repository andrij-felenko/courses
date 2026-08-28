from abc import ABC, abstractmethod

# КОМПОНЕНТ — спільний інтерфейс напою
class Beverage(ABC):
    @abstractmethod
    def cost(self) -> int: ...
    @abstractmethod
    def description(self) -> str: ...

# КОНКРЕТНИЙ КОМПОНЕНТ — проста кава
class Coffee(Beverage):
    def cost(self) -> int:        return 20
    def description(self) -> str: return "кава"

# БАЗОВИЙ ДЕКОРАТОР — тримає компонент і за замовчуванням делегує
class AddOn(Beverage):
    def __init__(self, inner: Beverage):
        self._inner = inner            # тип КОМПОНЕНТА — тому вкласти можна будь-що
    def cost(self) -> int:        return self._inner.cost()
    def description(self) -> str: return self._inner.description()

# КОНКРЕТНІ ДЕКОРАТОРИ — навколо делегації додають своє
class Milk(AddOn):
    def cost(self) -> int:        return self._inner.cost() + 5
    def description(self) -> str: return self._inner.description() + " + молоко"

class Cinnamon(AddOn):
    def cost(self) -> int:        return self._inner.cost() + 3
    def description(self) -> str: return self._inner.description() + " + кориця"

# СКЛАДАННЯ — обгортки нанизуються в рантаймі
order = Cinnamon(Milk(Coffee()))
order.description()  # "кава + молоко + кориця"
order.cost()         # 28
