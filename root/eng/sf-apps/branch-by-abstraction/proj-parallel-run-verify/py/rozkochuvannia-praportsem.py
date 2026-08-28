from typing import Protocol
import time

class Flags(Protocol):
    # Детермінований відсоток: той самий ключ+ідентифікатор → та сама відповідь,
    # тож один користувач стабільно або в тіні, або ні — не мерехтить від виклику до виклику.
    def sampled(self, key: str, id: str) -> bool: ...

class ComparingRenderer:
    def __init__(self, control, candidate, log, flags):
        self._control, self._candidate = control, candidate
        self._log, self._flags = log, flags

    def render(self, template, data):
        result = self._control.render(template, data)

        # У тінь потрапляє лише вибрана відсотком частка викликів
        if self._flags.sampled("render-shadow-percent", template):
            started = time.perf_counter()
            try:
                shadow = self._candidate.render(template, data)
                self._log.timing("candidate", time.perf_counter() - started)  # вартість
                if shadow != result:
                    self._log.mismatch(template=template, control=result, candidate=shadow)
            except Exception as err:
                self._log.candidate_threw(template=template, error=err)
        return result
