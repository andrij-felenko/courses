// adapters/memory.ts ── ДРАЙВОВАНИЙ АДАПТЕР. Той самий порт, але в пам'яті.
import { ЗамовленняСховище, Замовлення } from "../order/core";

export class ПамятьСховище implements ЗамовленняСховище {
  private дані = new Map<string, Замовлення>();

  async зберегти(з: Замовлення): Promise<void> {
    this.дані.set(з.id, з);            // усе «сховище» — одна мапа
  }

  async узяти(id: string): Promise<Замовлення | null> {
    return this.дані.get(id) ?? null;
  }
}
