from typing import Protocol

class Mediator(Protocol):
    def notify(self, sender: "Widget", event: str) -> None: ...

class Widget:                                     # КОЛЕГА
    def __init__(self, mediator: Mediator) -> None:
        self._m = mediator                        # знає лише посередника

class Checkbox(Widget):
    checked = False
    def toggle(self) -> None:
        self.checked = not self.checked
        self._m.notify(self, "toggled")           # «я змінився» — і все

class TextField(Widget):
    value = ""
    enabled = True
    def set_value(self, v: str) -> None:
        self.value = v
        self._m.notify(self, "typed")

class Button(Widget):
    enabled = False
    def render(self) -> None:
        print(f"[Оформити] {'активна' if self.enabled else 'згасла'}")
