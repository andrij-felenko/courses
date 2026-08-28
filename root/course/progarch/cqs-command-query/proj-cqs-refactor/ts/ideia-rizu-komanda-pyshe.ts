type Money = number;                 // у копійках, щоб не губити точність на дробах

class EnergyService {
  private readings = new Map<string, number[]>();
  constructor(
    private readonly tariff: Money,        // копійок за 1 кВт·год
    private readonly standing: Money = 0,  // фіксована абонплата
  ) {}

  // КОМАНДА: дописала показник — і мовчить
  record(deviceId: string, kWh: number): void {
    const list = this.readings.get(deviceId) ?? [];
    list.push(kWh);
    this.readings.set(deviceId, list);
  }

  // ЗАПИТ: рахунок — чиста функція від збережених показників
  projectedBill(deviceId: string): Money {
    const kWh = (this.readings.get(deviceId) ?? []).reduce((a, b) => a + b, 0);
    return Math.round(kWh * this.tariff) + this.standing;
  }

  // ЗАПИТ: скільки показників лежить — знадобиться в тестах
  readingCount(deviceId: string): number {
    return this.readings.get(deviceId)?.length ?? 0;
  }
}
