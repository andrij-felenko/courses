# routing/domain/shipment.py — поняття предмета, мова перевізника
from dataclasses import dataclass

@dataclass(frozen=True)
class TimeWindow:
    frm: int   # хвилини від початку доби, напр. 540 = 09:00
    to: int    # 1020 = 17:00

@dataclass(frozen=True)
class Shipment:
    id: str
    address: str
    weight_kg: float
    window: TimeWindow

    def __post_init__(self):
        if self.weight_kg <= 0:
            raise ValueError("вага відправлення має бути додатною")
        if self.window.frm >= self.window.to:
            raise ValueError("порожнє вікно доставки")

# routing/domain/route.py — маршрут однієї машини; сам боронить своє правило
class Route:
    def __init__(self, vehicle_id: str, capacity_kg: float):
        self.vehicle_id = vehicle_id
        self.capacity_kg = capacity_kg
        self._stops: list[Shipment] = []
        self._load_kg = 0.0

    def try_add(self, s: Shipment) -> bool:
        if self._load_kg + s.weight_kg > self.capacity_kg:
            return False                       # не влазить
        self._stops.append(s)
        self._load_kg += s.weight_kg
        return True

    @property
    def shipments(self) -> list[Shipment]:
        return list(self._stops)

    @property
    def fill_ratio(self) -> float:
        return self._load_kg / self.capacity_kg
