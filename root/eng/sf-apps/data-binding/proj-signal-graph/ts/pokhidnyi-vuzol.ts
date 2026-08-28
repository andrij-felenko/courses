// ── 2. Похідний вузол ─────────────────────────────────────────────────
class Derived<T> extends Node {
  deps = new Set<Node>();       // кого читав ОСТАННЬОГО разу
  markedAt = 0;                 // епоха, у якій позначено застарілим
  settledAt = 0;                // епоха, у якій уже влігся
  private value!: T;
  private fresh = false;        // чи обчислювали хоч раз
  private running = false;      // проти циклу в графі

  constructor(private fn: () => T, private eq: Eq<T> = Object.is) { super(); }

  get(): T {
    if (this.running) throw new Error('цикл у графі: вузол читає сам себе');
    if (!this.fresh) this.recompute();   // перше читання й заводить вузол у граф
    else settleNode(this);               // до нас дійшли раніше за чергу — влягаємось тут-таки
    track(this);
    return this.value;
  }

  /** Виконує вираз, перезбирає підписки й висоту; true — значення змінилося. */
  recompute(): boolean {
    const before = this.deps;
    this.deps = new Set();

    const outer = frame;
    frame = this;
    this.running = true;
    let next: T;
    try { next = this.fn(); }
    finally { this.running = false; frame = outer; }

    for (const d of before)                          // зняти те, чого цього разу НЕ читали
      if (!this.deps.has(d)) d.subs.delete(this);

    let h = 0;
    for (const d of this.deps) h = Math.max(h, d.height + 1);
    this.height = h;

    const changed = !this.fresh || !this.eq(next, this.value);
    this.value = next;
    this.fresh = true;
    if (changed) this.changedAt = epoch;
    return changed;
  }

  dispose(): void {                                  // зняти себе з усіх входів
    for (const d of this.deps) d.subs.delete(this);
    this.deps.clear();
  }
}

const signal   = <T>(v: T, eq?: Eq<T>) => new Source(v, eq);
const computed = <T>(fn: () => T, eq?: Eq<T>) => new Derived(fn, eq);

/** Ефект — лист графа, що робить видиму роботу й нічого не віддає далі. */
function effect(run: () => void): () => void {
  const node = new Derived<void>(run, () => true);   // «значення» ефекту не змінюється ніколи
  node.recompute();                                  // перший прогін і підписує
  return () => node.dispose();
}
