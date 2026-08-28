class Thermostat:                    # МОДЕЛЬ: дані + правило, і нічого про екран
    def __init__(self):
        self._target = 22
        self._observers = []         # хто хоче знати про зміни — не знаю хто саме

    @property
    def target(self):
        return self._target

    def nudge(self, delta):          # правило предметної області живе тут
        self._target = max(5, min(30, self._target + delta))
        for notify in self._observers:   # сповістити залежних, не знаючи, хто вони
            notify()

    def on_change(self, fn):
        self._observers.append(fn)
