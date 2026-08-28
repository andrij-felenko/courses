// domain/order.ts — правила предметної області, і більш нічого
export enum Promo { None = 1.0, Spring = 0.9, Vip = 0.8 }

export interface Line {
  readonly sku: string;
  readonly qty: number;
  readonly price: number;   // ціну домен отримує ззовні, сам її не шукає
}

export class Order {
  constructor(
    readonly lines: Line[],
    readonly promo: Promo = Promo.None,
  ) {}

  total(): number {
    const raw = this.lines.reduce((s, l) => s + l.price * l.qty, 0);
    return Math.round(raw * this.promo * 100) / 100;
  }
}
