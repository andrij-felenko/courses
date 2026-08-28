class FreshnessGuard:                 # обгортка над портом Sensor: ловить ЗАСТИГЛИЙ давач
    def __init__(self, inner: Sensor, limit=10):
        self._inner, self._limit = inner, limit
        self._last, self._same = None, 0
    def read(self) -> Reading:
        r = self._inner.read()
        if not r.ok:                              # уже визнаний збій — пропускаємо як є
            self._same = 0
            return r
        self._same = self._same + 1 if r.celsius == self._last else 0
        self._last = r.celsius
        if self._same >= self._limit:             # надто довго те саме число → застигло
            return Reading(celsius=r.celsius, ok=False)   # доводимо застиглість до «не вірю»
        return r
