// 1. новий клас — ПОРУЧ, окремим файлом, наявне не відкриваємо
class PostalRate implements ShippingStrategy {
  cost(s: Shipment): number {
    return weightFee(30, s, 12);          // переуживає той самий помічник
  }
}

// 2. один рядок у таблиці
const STRATEGIES: Record<Carrier, ShippingStrategy> = {
  flat:      new FlatRate(),
  zonal:     new ZonalRate(),
  free_over: new FreeOverThreshold(),
  courier:   new CourierRate(),
  postal:    new PostalRate(),           // ← усе, що додали
};
// (+ "postal" у тип Carrier)
