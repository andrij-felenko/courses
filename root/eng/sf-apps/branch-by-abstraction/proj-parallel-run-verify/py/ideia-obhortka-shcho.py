from typing import Protocol, Any

class Renderer(Protocol):
    def render(self, template: str, data: dict[str, Any]) -> str: ...

# Звіряч — сам реалізація шва, тримає стару (control) й нову (candidate)
class ComparingRenderer:
    def __init__(self, control: Renderer, candidate: Renderer, log: "MismatchLog"):
        self._control = control      # стара, їй довіряємо — її вихід іде клієнтові
        self._candidate = candidate  # нова, у тіні
        self._log = log

    def render(self, template: str, data: dict[str, Any]) -> str:
        result = self._control.render(template, data)   # це піде користувачеві

        # Нова — в тіні. Її помилка НЕ сміє зачепити користувача,
        # тож ловимо все, що вона кине, і трактуємо як розбіжність.
        try:
            shadow = self._candidate.render(template, data)
            if shadow != result:
                self._log.mismatch(template=template, control=result, candidate=shadow)
        except Exception as err:
            self._log.candidate_threw(template=template, error=err)

        return result               # завжди повертаємо перевірене
