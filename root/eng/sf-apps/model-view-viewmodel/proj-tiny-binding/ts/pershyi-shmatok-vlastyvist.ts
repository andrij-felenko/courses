// ── 1. Сигнали: словник «ім'я властивості → хто це слухає» ──
type Listener = (value: unknown) => void;

class Signals {
  private subs = new Map<string, Set<Listener>>();

  on(prop: string, fn: Listener): () => void {
    let set = this.subs.get(prop);
    if (!set) this.subs.set(prop, (set = new Set()));
    set.add(fn);
    return () => { set!.delete(fn); };          // повертаємо «відписку»
  }

  emit(prop: string, value: unknown): void {
    const set = this.subs.get(prop);
    if (!set) return;
    for (const fn of [...set]) fn(value);       // копія: слухач може відписатися просто в обході
  }
}

/** Підмінює КОЖНЕ власне поле об'єкта парою get/set із сигналом. */
function observable<T extends object>(vm: T): T & { signals: Signals } {
  const signals = new Signals();
  for (const key of Object.keys(vm)) {
    let value = (vm as any)[key];               // значення переїжджає в замикання
    Object.defineProperty(vm, key, {
      enumerable: true,
      configurable: true,
      get: () => value,
      set: (next) => {
        if (Object.is(next, value)) return;     // не змінилось — не сповіщаємо
        value = next;
        signals.emit(key, next);
      },
    });
  }
  return Object.assign(vm, { signals });
}
