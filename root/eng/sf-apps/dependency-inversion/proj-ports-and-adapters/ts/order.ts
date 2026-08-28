// domain/order.ts ── СУТНІСТЬ і правила. Не імпортує нічого зовнішнього.
export interface Line { sku: string; price: number; qty: number; }

export class DomainError extends Error {}

export class Order {
  private constructor(
    readonly id: string,
    readonly email: string,
    readonly lines: Line[],
  ) {}

  static place(id: string, email: string, lines: Line[]): Order {
    if (lines.length === 0) throw new DomainError("порожнє замовлення");   // ПРАВИЛО
    if (!email.includes("@")) throw new DomainError("недійсна пошта");      // ПРАВИЛО
    return new Order(id, email, lines);
  }

  total(): number {
    return this.lines.reduce((s, l) => s + l.price * l.qty, 0);            // ПРАВИЛО
  }
}
