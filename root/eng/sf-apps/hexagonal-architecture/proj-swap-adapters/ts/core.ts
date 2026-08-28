// order/core.ts ── ЯДРО. Не імпортує НІЧОГО зовнішнього.

export interface Позиція { товар: string; ціна: number; кількість: number; }

export class Замовлення {
  private constructor(
    readonly id: string,
    readonly пошта: string,
    readonly позиції: Позиція[],
  ) {}

  static створити(id: string, пошта: string, позиції: Позиція[]): Замовлення {
    if (позиції.length === 0) throw new Error("порожнє замовлення");     // ПРАВИЛО
    if (!пошта.includes("@")) throw new Error("недійсна пошта");         // ПРАВИЛО
    return new Замовлення(id, пошта, позиції);
  }

  сума(): number {
    return this.позиції.reduce((s, п) => s + п.ціна * п.кількість, 0);   // ПРАВИЛО
  }
}

// ── ПОРТИ ──
// Вхідний: що ядро ПРОПОНУЄ світу
export interface ОформленняЗамовлення {
  оформити(пошта: string, позиції: Позиція[]): Promise<Замовлення>;
}
// Вихідний: що ядро ВИМАГАЄ від світу — рівно два дієслова, мовою домену
export interface ЗамовленняСховище {
  зберегти(з: Замовлення): Promise<void>;
  узяти(id: string): Promise<Замовлення | null>;
}
