class Thermostat:
    MIN, MAX = 5, 30

    def __init__(self, target=22):
        self._target = self._clamp(target)
        self._observers = []                 # хто хоче знати про зміни — не знаю хто

    @property
    def target(self):
        return self._target

    def nudge(self, delta):
        new = self._clamp(self._target + delta)
        if new == self._target:
            return                           # нічого не змінилось — нікого не турбуємо
        self._target = new
        for notify in self._observers:       # сповістити залежних, не називаючи їх
            notify()

    def on_change(self, fn):
        self._observers.append(fn)

    @staticmethod
    def _clamp(t):
        return max(Thermostat.MIN, min(Thermostat.MAX, t))
