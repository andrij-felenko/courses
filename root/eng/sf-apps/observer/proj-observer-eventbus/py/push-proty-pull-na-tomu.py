# PUSH-варіант: суб'єкт штовхає готові дані в аргумент.
class PushObserver(Protocol):
    def update(self, reading: Reading) -> None: ...   # отримує ДАНІ, не суб'єкт


class PushStation:
    def __init__(self) -> None:
        self._observers: list[PushObserver] = []
        self._reading = Reading(0.0, 0.0)
        # (прапорці й копія списку — так само, як вище; тут опущено)

    def subscribe(self, o: PushObserver) -> None:
        if o not in self._observers:
            self._observers.append(o)

    def _notify(self) -> None:
        payload = self._reading                    # конверт події
        for o in list(self._observers):
            try:
                o.update(payload)                  # дані летять В аргументі
            except Exception:
                log.exception("push-спостерігач упав")

    def set_reading(self, temp: float, humidity: float) -> None:
        self._reading = Reading(temp, humidity)
        self._notify()


class PushDisplay:
    def update(self, reading: Reading) -> None:    # бере, що дали, не питає
        print(f"Табло: {reading.temp}°C")
