class Thermostat {
  static readonly MIN = 5;
  static readonly MAX = 30;

  #target: number;
  #observers: Array<() => void> = [];        // хто хоче знати — не знаю хто

  constructor(target = 22) {
    this.#target = Thermostat.clamp(target);
  }

  get target(): number { return this.#target; }

  nudge(delta: number): void {
    const next = Thermostat.clamp(this.#target + delta);
    if (next === this.#target) return;       // нічого не змінилось — нікого не турбуємо
    this.#target = next;
    for (const notify of this.#observers) notify();   // сповістити залежних
  }

  onChange(fn: () => void): void { this.#observers.push(fn); }

  private static clamp(t: number): number {
    return Math.max(Thermostat.MIN, Math.min(Thermostat.MAX, t));
  }
}
