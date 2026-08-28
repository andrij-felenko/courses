// routing/domain/Shipment.ts — поняття предмета, мова перевізника
export interface TimeWindow {
  from: number;  // хвилини від початку доби, напр. 540 = 09:00
  to: number;    // 1020 = 17:00
}

export class Shipment {
  constructor(
    public readonly id: string,
    public readonly address: string,
    public readonly weightKg: number,
    public readonly window: TimeWindow,
  ) {
    if (weightKg <= 0) throw new Error("вага відправлення має бути додатною");
    if (window.from >= window.to) throw new Error("порожнє вікно доставки");
  }
}

// routing/domain/Route.ts — маршрут однієї машини; сам боронить своє правило
export class Route {
  private readonly stops: Shipment[] = [];
  private loadKg = 0;

  constructor(
    public readonly vehicleId: string,
    public readonly capacityKg: number,
  ) {}

  tryAdd(s: Shipment): boolean {
    if (this.loadKg + s.weightKg > this.capacityKg) return false; // не влазить
    this.stops.push(s);
    this.loadKg += s.weightKg;
    return true;
  }

  get shipments(): readonly Shipment[] { return this.stops; }
  get fillRatio(): number { return this.loadKg / this.capacityKg; }
}
