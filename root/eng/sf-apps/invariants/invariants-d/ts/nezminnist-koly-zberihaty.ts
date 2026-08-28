class TempRange {
  readonly min: number;
  readonly max: number;
  constructor(min: number, max: number) {
    if (min > max) throw new Error("min не може бути більший за max");
    this.min = min; this.max = max;      // перевірили ОДИН раз — і назавжди
  }
  // «Зміна» = новий об'єкт, що знову проходить перевірку конструктора.
  withMin(v: number): TempRange { return new TempRange(v, this.max); }
}
