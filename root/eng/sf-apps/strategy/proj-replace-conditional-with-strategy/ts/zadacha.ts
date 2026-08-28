type Carrier = "flat" | "zonal" | "free_over" | "courier";

class Shipment {
  constructor(
    public carrier: Carrier,
    public weightKg: number,
    public distanceKm: number,
    public orderTotal: number,
    public express: boolean,
  ) {}

  shippingCost(): number {
    // ← пахучий метод: усі служби зашиті в один switch
    switch (this.carrier) {
      case "flat":
        return 50 + this.weightKg * 10;

      case "zonal": {
        const zone = Math.ceil(this.distanceKm / 100); // 1 зона = 100 км
        return 40 + zone * 25;
      }

      case "free_over":
        if (this.orderTotal >= 1000) return 0;
        return 60 + this.weightKg * 8;

      case "courier": {
        const base = 80 + this.distanceKm * 1.5;
        return this.express ? base * 1.6 : base;
      }

      default:
        throw new Error(`Невідома служба: ${this.carrier}`);
    }
  }
}
