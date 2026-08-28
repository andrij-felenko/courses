class FlatRate implements ShippingStrategy {
  cost(s: Shipment): number {
    return 50 + s.weightKg * 10;
  }
}

class ZonalRate implements ShippingStrategy {
  cost(s: Shipment): number {
    const zone = Math.ceil(s.distanceKm / 100);
    return 40 + zone * 25;
  }
}

class FreeOverThreshold implements ShippingStrategy {
  cost(s: Shipment): number {
    if (s.orderTotal >= 1000) return 0;
    return 60 + s.weightKg * 8;
  }
}

class CourierRate implements ShippingStrategy {
  cost(s: Shipment): number {
    const base = 80 + s.distanceKm * 1.5;
    return s.express ? base * 1.6 : base;
  }
}
