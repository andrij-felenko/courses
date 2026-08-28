# спільна арифметика живе ВБІК — як інструмент, не як предок
def weight_fee(base: float, s: "Shipment", per_kg: float) -> float:
    return base + s.weight_kg * per_kg

class FlatRate(ShippingStrategy):
    def cost(self, s):
        return weight_fee(50, s, 10)            # кличе спільне

class FreeOverThreshold(ShippingStrategy):
    def cost(self, s):
        if s.order_total >= 1000:              # СВОЯ, відмінна умова лишається тут
            return 0.0
        return weight_fee(60, s, 8)            # а спільну частину — переуживає
