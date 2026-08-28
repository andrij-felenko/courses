// Джерело бандла (центр політики).
interface BundleSource {
  pull(sinceRevision: string): Promise<PolicyBundle | null>;  // null = 304, без змін
  verify(bundle: PolicyBundle): boolean;                      // підпис бандла зійшовся?
}

// Гарячий шлях бачить лише policy() — читання вказівника, БЕЗ I/O. Уся мережа — у фоні.
interface PolicySource { policy(): Policy; }

class PolicyProvider implements PolicySource {
  private current: Policy | null = null;   // null, доки не прийшов перший валідний бандл
  private revision = "";

  constructor(private src: BundleSource, private intervalMs = 30_000) {}

  policy(): Policy {
    if (!this.current) throw new Error("policy-not-loaded"); // старт без правила: нема чому дозволяти
    return this.current;
  }

  async refreshOnce(): Promise<void> {
    const bundle = await this.src.pull(this.revision);
    if (!bundle) return;                       // 304: нема нового — лишаємо чинне
    if (!this.src.verify(bundle)) return;      // підпис не зійшовся → НЕ активуємо
    this.current = compilePolicy(bundle);      // атомарна підміна вказівника — запит не помітив
    this.revision = bundle.version;
  }

  start(): void {                              // фоновий цикл, окремо від запитів
    const tick = async () => {
      try { await this.refreshOnce(); }
      catch { /* збій тягання → лишаємо останнє добре відоме правило (fail-static) */ }
      finally { setTimeout(tick, this.intervalMs); }
    };
    void tick();
  }
}
