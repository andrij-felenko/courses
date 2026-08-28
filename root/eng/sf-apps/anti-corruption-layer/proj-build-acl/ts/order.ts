// domain/order.ts — НАШ світ. Мова складу. Про CRM не чув.
export class Article { constructor(readonly code: string) {} }
export class Color   { static parse(s: string) { return new Color(s); }
                       private constructor(readonly name: string) {} }
export class Size    { static parse(s: string) { return new Size(s); }
                       private constructor(readonly label: string) {} }
export class ClientId { constructor(readonly value: string) {} }

export class Product {
  constructor(
    readonly article: Article,
    readonly color: Color,
    readonly size: Size,
  ) {}
}

export class Order {
  constructor(
    readonly client: ClientId,
    readonly product: Product,
    readonly quantity: number,  // завжди > 0 — модель від'ємних не знає
  ) {}
  reserve(): void { /* чисте доменне правило складу */ }
}

// Порт: що домен ВИМАГАЄ. Оголошено нашою мовою.
export interface OrderSource {
  next(): Order | null;
}
