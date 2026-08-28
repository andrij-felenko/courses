export class Metrics {
  // у Node цикл подій однопотоковий — замок тут не потрібен і був би обманом
  private readonly counts = new Map<string, number>();

  bump(name: string): void {
    this.counts.set(name, (this.counts.get(name) ?? 0) + 1);
  }

  value(name: string): number {
    return this.counts.get(name) ?? 0;
  }
}
