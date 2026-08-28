// спільна арифметика живе ВБІК — як інструмент, не як предок
function weightFee(base: number, s: Shipment, perKg: number): number {
  return base + s.weightKg * perKg;
}

class FlatRate implements ShippingStrategy {
  cost(s: Shipment): number {
    return weightFee(50, s, 10);            // кличе спільне
  }
}

class FreeOverThreshold implements ShippingStrategy {
  cost(s: Shipment): number {
    if (s.orderTotal >= 1000) return 0;     // СВОЯ, відмінна умова лишається тут
    return weightFee(60, s, 8);             // а спільну частину — переуживає
  }
}
