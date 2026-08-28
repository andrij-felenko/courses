// мапа «тип → стратегія» замість switch — будується ОДИН раз
const STRATEGIES: Record<Carrier, ShippingStrategy> = {
  flat:      new FlatRate(),
  zonal:     new ZonalRate(),
  free_over: new FreeOverThreshold(),
  courier:   new CourierRate(),
};

class Shipment {
  constructor(
    public carrier: Carrier,
    public weightKg: number,
    public distanceKm: number,
    public orderTotal: number,
    public express: boolean,
  ) {}

  shippingCost(): number {
    const strategy = STRATEGIES[this.carrier];        // пошук замість switch
    if (!strategy) throw new Error(`Невідома служба: ${this.carrier}`);
    return strategy.cost(this);                        // делегуємо, не знаючи, яка саме
  }
}
