# мапа «тип → стратегія» замість if-ланцюга — будується ОДИН раз
STRATEGIES: dict[str, ShippingStrategy] = {
    "flat":      FlatRate(),
    "zonal":     ZonalRate(),
    "free_over": FreeOverThreshold(),
    "courier":   CourierRate(),
}

@dataclass
class Shipment:
    carrier: str
    weight_kg: float
    distance_km: float
    order_total: float
    express: bool

    def shipping_cost(self) -> float:
        strategy = STRATEGIES.get(self.carrier)       # пошук замість if-ланцюга
        if strategy is None:
            raise ValueError(f"Невідома служба: {self.carrier}")
        return strategy.cost(self)                     # делегуємо, не знаючи, яка саме
