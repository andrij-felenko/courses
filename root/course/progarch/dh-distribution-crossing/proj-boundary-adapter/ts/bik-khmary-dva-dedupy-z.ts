// ── БІК ХМАРИ: тут живе дедуп — друга половина «фактично раз». ──
class CloudServer {
  private seen   = new Map<string, Result>(); // ключ ідемпотентності → кешований результат
  private lastTS = new Map<string, number>(); // dev|field → найсвіжіша бачена мітка
  private state  = new Map<string, string>(); // dev → востаннє почуте значення
  executed = 0;                               // скільки КОМАНД реально виконано
  applied  = 0;                               // скільки ЗВІТІВ реально застосовано

  // Команда: той самий ключ → той самий результат, дію НЕ повторюємо.
  handleCmd(cmd: Command): Result {
    const hit = this.seen.get(cmd.key);
    if (hit) return hit;                       // ДУБЛЬ повтору — нічого не робимо
    this.executed++;                           // виконуємо РІВНО раз
    if (cmd.kind === "setState") this.state.set(cmd.dev, cmd.arg ?? "");
    const r: Result = { ok: true, note: `виконано ${cmd.kind}` };
    this.seen.set(cmd.key, r);
    return r;
  }

  // Звіт: одне правило ловить і дубль, і спізнілий реордер.
  handleReport(rep: Report): void {
    const k = `${rep.dev}|${rep.field}`;
    if (rep.ts <= (this.lastTS.get(k) ?? 0)) return; // ≤ бачене → дубль АБО старіший реордер
    this.lastTS.set(k, rep.ts);                      // свіжіша мітка виграла
    this.state.set(rep.dev, rep.value);
    this.applied++;
  }
  get(dev: string): string { return this.state.get(dev) ?? ""; }
}
