from math import ceil

class FlatRate(ShippingStrategy):
    def cost(self, s):
        return 50 + s.weight_kg * 10

class ZonalRate(ShippingStrategy):
    def cost(self, s):
        zone = ceil(s.distance_km / 100)
        return 40 + zone * 25

class FreeOverThreshold(ShippingStrategy):
    def cost(self, s):
        if s.order_total >= 1000:
            return 0.0
        return 60 + s.weight_kg * 8

class CourierRate(ShippingStrategy):
    def cost(self, s):
        base = 80 + s.distance_km * 1.5
        return base * 1.6 if s.express else base
