class TempRange:
    def __init__(self, minimum: float, maximum: float) -> None:
        # встановлюємо інваріант: без коректних меж об'єкт не народжується.
        if minimum > maximum:
            raise ValueError("min не може бути більший за max")
        self._min = minimum      # стан прихований (умовно приватний)
        self._max = maximum

    def set_min(self, v: float) -> None:
        # Кожна операція зберігає інваріант.
        if v > self._max:
            raise ValueError("min не може перевищити max")
        self._min = v

    def width(self) -> float:
        return self._max - self._min          # завжди ≥ 0 — гарантовано

    def contains(self, t: float) -> bool:
        return self._min <= t <= self._max
