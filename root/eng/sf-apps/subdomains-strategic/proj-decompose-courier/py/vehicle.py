# fleet/domain/vehicle.py — допоміжне: чесно, надійно, без вилизування
class Vehicle:
    def __init__(self, id: str, capacity_kg: float,
                 odometer_km: float, next_service_km: float):
        self.id = id
        self.capacity_kg = capacity_kg
        self._odometer_km = odometer_km
        self._next_service_km = next_service_km

    def needs_service(self) -> bool:
        return self._odometer_km >= self._next_service_km

    def add_trip(self, km: float) -> None:
        self._odometer_km += km
