// ── 2. ЖИВА СЕСІЯ ДОМУ (актор): кеш-координатор над рядком, НЕ джерело правди ──
class HomeSession {
  private twin: Twin | null = null;      // порожньо, доки не гідратуємось
  private box: Cmd[] = [];               // пошта: серіалізує команди дому
  private busy = false;
  constructor(readonly homeId: string, private store: ShardStore, private audit: AuditLog) {}

  // ГІДРАТАЦІЯ: наповнити сесію станом із ДЖЕРЕЛА ПРАВДИ при виході на зв'язок
  hydrate(): void { this.twin = this.store.get(this.homeId); }   // ← увесь «відновлення стану»

  // ЄДИНИЙ вхід для команд: покласти в пошту й розбудити цикл
  tell(cmd: Cmd): void { this.box.push(cmd); this.pump(); }

  private pump(): void {
    if (this.busy) return;               // вже крутиться — новий tell лише долив у чергу
    this.busy = true;
    while (this.box.length) this.apply(this.box.shift()!);   // одне за раз, до кінця
    this.busy = false;
  }

  private apply(cmd: Cmd): void {
    if (!this.twin) throw new Error("сесію не гідратовано");
    // (a) новий стан у кеші — версія росте
    const next: Twin = {
      homeId: this.homeId,
      version: this.twin.version + 1,
      bolt: cmd.kind === "lock" ? "locked" : "unlocked",
      lastCmd: `${cmd.by}#${cmd.seq}`,
    };
    // (b) НАСКРІЗНИЙ запис у ДЖЕРЕЛО ПРАВДИ (CAS по version)
    if (!this.store.putCas(next, this.twin.version)) {
      this.hydrate();                    // хтось випередив → перечитати правду…
      return this.apply(cmd);            // …і повторити команду на свіжому стані
    }
    // (c) дописати ФАКТ у журнал аудиту (лише замки)
    this.audit.append({ homeId: this.homeId, action: next.bolt, by: cmd.by, at: Date.now() });
    // (d) аж ТЕПЕР зафіксувати кеш → read-your-writes: кеш == довговічний рядок
    this.twin = next;
  }

  snapshot(): Twin { return this.twin!; }              // тепле читання: з живого актора
}
