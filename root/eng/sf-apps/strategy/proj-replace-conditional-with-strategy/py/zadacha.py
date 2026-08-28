from math import ceil
from dataclasses import dataclass

@dataclass
class Shipment:
    carrier: str          # "flat" | "zonal" | "free_over" | "courier"
    weight_kg: float
    distance_km: float
    order_total: float
    express: bool

    def shipping_cost(self) -> float:
        # ← пахучий метод: усі служби зашиті в один if-ланцюг
        if self.carrier == "flat":
            return 50 + self.weight_kg * 10

        if self.carrier == "zonal":
            zone = ceil(self.distance_km / 100)   # 1 зона = 100 км
            return 40 + zone * 25

        if self.carrier == "free_over":
            if self.order_total >= 1000:
                return 0.0
            return 60 + self.weight_kg * 8

        if self.carrier == "courier":
            base = 80 + self.distance_km * 1.5
            return base * 1.6 if self.express else base

        raise ValueError(f"Невідома служба: {self.carrier}")
