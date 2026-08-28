from typing import Protocol

class Observer(Protocol):
    def update(self, subject: "WeatherStation") -> None: ...

class WeatherStation:                        # СУБ'ЄКТ
    def __init__(self) -> None:
        self._observers: set[Observer] = set()   # список підписників
        self._temp = 0.0

    def subscribe(self, o: Observer) -> None:   self._observers.add(o)
    def unsubscribe(self, o: Observer) -> None: self._observers.discard(o)

    def _notify(self) -> None:                # серце патерна
        for o in self._observers:
            o.update(self)

    def set_temp(self, t: float) -> None:     # ось тут стан змінюється
        self._temp = t
        self._notify()                        # ...і одразу летить сигнал

    @property
    def temp(self) -> float:
        return self._temp

class Display:                                # конкретний СПОСТЕРІГАЧ
    def update(self, station: "WeatherStation") -> None:
        print(f"Табло: {station.temp}°C")
