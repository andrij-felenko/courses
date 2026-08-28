type Version = number;
type Rec = { value: unknown; version: Version };

// Одна копія дому. Знає лише те, що вже до неї доїхало.
class Replica {
  private data = new Map<string, Rec>();
  linked = true;                         // чи доходять оновлення від лідера (false — у розкол)
  constructor(readonly id: string) {}

  local(key: string): Rec | undefined { return this.data.get(key); }

  // Монотонність версій: приймаємо лише СВІЖІШЕ; старий кадр не затирає нового.
  apply(key: string, rec: Rec): void {
    const cur = this.data.get(key);
    if (cur === undefined || rec.version > cur.version) this.data.set(key, rec);
  }
}
