// fleet/domain/Vehicle.ts — допоміжне: чесно, надійно, без вилизування
export class Vehicle {
  constructor(
    public readonly id: string,
    public readonly capacityKg: number,
    private odometerKm: number,
    private nextServiceKm: number,
  ) {}

  needsService(): boolean { return this.odometerKm >= this.nextServiceKm; }
  addTrip(km: number): void { this.odometerKm += km; }
}
