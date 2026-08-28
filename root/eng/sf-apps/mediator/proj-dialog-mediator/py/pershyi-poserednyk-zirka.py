from typing import Protocol

class Mediator(Protocol):
    def notify(self, sender: str, event: str) -> None: ...   # НАЇВНО: рядок

class Field:                            # текстове поле-колега
    def __init__(self, id: str, m: Mediator) -> None:
        self.id, self._m = id, m
        self.value, self.enabled, self.error = "", True, ""
    def set_value(self, v: str) -> None:
        self.value = v
        self._m.notify(self.id, "changed")

class Check:                            # прапорець-колега
    def __init__(self, id: str, m: Mediator) -> None:
        self.id, self._m = id, m
        self.checked = False
    def toggle(self) -> None:
        self.checked = not self.checked
        self._m.notify(self.id, "toggled")

class Select(Field):                    # список — поле плюс набір варіантів
    def __init__(self, id: str, m: Mediator) -> None:
        super().__init__(id, m)
        self.options: list[str] = []
    def set_options(self, o: list[str]) -> None:
        self.options = o
        if self.value not in o:
            self.value = ""             # старий вибір більше не чинний
