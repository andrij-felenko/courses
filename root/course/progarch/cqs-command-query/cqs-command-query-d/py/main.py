class TelemetryLog:
    def __init__(self) -> None:
        self._readings: list[float] = []

    def append(self, reading: float) -> None:   # КОМАНДА: змінює стан
        self._readings.append(reading)

    def average(self) -> float:                 # ЗАПИТ: тільки читає
        if not self._readings:
            return 0.0
        return sum(self._readings) / len(self._readings)
