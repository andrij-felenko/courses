class FreshnessGuard:                    # обгортка над портом Sensor — той самий інтерфейс
    def __init__(self, inner: Sensor, stale_after: int = 3):
        self._inner = inner
        self._stale_after = stale_after
        self._last: float | None = None  # останнє число, якому повірили
        self._same = 0                   # скільки разів ПОСПІЛЬ воно повторилось

    def read(self) -> Reading:
        r = self._inner.read()
        if not r.ok:                     # уже чесний збій — не наша турбота, лічильник з нуля
            self._same = 0
            return r
        self._same = self._same + 1 if r.celsius == self._last else 0
        self._last = r.celsius
        if self._same >= self._stale_after:          # застій переріс дозволене → «не вірю»
            return Reading(celsius=r.celsius, ok=False)
        return r
