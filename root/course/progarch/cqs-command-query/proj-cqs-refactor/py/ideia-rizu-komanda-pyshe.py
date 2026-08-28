class EnergyService:
    def __init__(self, tariff: int, standing: int = 0) -> None:
        self._readings: dict[str, list[float]] = {}
        self._tariff = tariff          # копійок за 1 кВт·год
        self._standing = standing      # фіксована абонплата

    def record(self, device_id: str, kwh: float) -> None:      # КОМАНДА
        self._readings.setdefault(device_id, []).append(kwh)

    def projected_bill(self, device_id: str) -> int:           # ЗАПИТ
        kwh = sum(self._readings.get(device_id, ()))
        return round(kwh * self._tariff) + self._standing

    def reading_count(self, device_id: str) -> int:            # ЗАПИТ
        return len(self._readings.get(device_id, ()))
