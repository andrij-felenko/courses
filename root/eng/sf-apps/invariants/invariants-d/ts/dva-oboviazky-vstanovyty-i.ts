class TempRange {
  // Стан прихований — ззовні межі не переписати повз перевірку.
  #min: number;
  #max: number;

  constructor(min: number, max: number) {
    // встановлюємо інваріант: без коректних меж об'єкт не народжується.
    if (min > max) throw new Error("min не може бути більший за max");
    this.#min = min;
    this.#max = max;
  }

  // Кожна операція зберігає інваріант.
  setMin(v: number): void {
    if (v > this.#max) throw new Error("min не може перевищити max");
    this.#min = v;
  }

  width(): number { return this.#max - this.#min; }   // завжди ≥ 0 — гарантовано
  contains(t: number): boolean { return this.#min <= t && t <= this.#max; }
}
