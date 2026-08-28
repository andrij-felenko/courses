// TypeScript: Повноцінний реактивний граф без глітчів із динамічними залежностями та batch

export interface Subscriber {
  markDirty(): void;
  run(): void;
}

export interface Dependency {
  removeSubscriber(sub: Subscriber): void;
}

// ── Глобальний контекст виконання ────────────────────────────────────────────
let activeSubscriber: (Subscriber & { addDependency(dep: Dependency): void }) | null = null;
const subscriberStack: typeof activeSubscriber[] = [];

let batchDepth = 0;
const pendingEffects = new Set<Subscriber>();

export function pushContext(sub: typeof activeSubscriber): void {
  subscriberStack.push(activeSubscriber);
  activeSubscriber = sub;
}

export function popContext(): void {
  activeSubscriber = subscriberStack.pop() ?? null;
}

export function batch<T>(fn: () => T): T {
  batchDepth++;
  try {
    return fn();
  } finally {
    batchDepth--;
    if (batchDepth === 0) {
      // Виконуємо всі відкладені ефекти після завершення пакета
      const effectsToRun = Array.from(pendingEffects);
      pendingEffects.clear();
      for (const effect of effectsToRun) {
        effect.run();
      }
    }
  }
}

// ── 1. Signal (Джерело первинного стану) ──────────────────────────────────────
export class Signal<T> implements Dependency {
  private value: T;
  private subscribers = new Set<Subscriber>();

  constructor(initialValue: T) {
    this.value = initialValue;
  }

  get(): T {
    if (activeSubscriber) {
      this.subscribers.add(activeSubscriber);
      activeSubscriber.addDependency(this);
    }
    return this.value;
  }

  set(newValue: T): void {
    if (Object.is(this.value, newValue)) return;
    this.value = newValue;

    // Фаза 1: Push (позначаємо залежні вузли брудними)
    const subs = Array.from(this.subscribers);
    for (const sub of subs) {
      sub.markDirty();
    }

    // Фаза 2: Запуск споживачів (або відкладення при batch)
    for (const sub of subs) {
      if (batchDepth > 0) {
        pendingEffects.add(sub);
      } else {
        sub.run();
      }
    }
  }

  removeSubscriber(sub: Subscriber): void {
    this.subscribers.delete(sub);
  }
}

export function createSignal<T>(initial: T): [() => T, (val: T) => void] {
  const s = new Signal(initial);
  return [() => s.get(), (val: T) => s.set(val)];
}

// ── 2. Computed (Мемоізоване похідне обчислення) ─────────────────────────────
export class Computed<T> implements Subscriber, Dependency {
  private fn: () => T;
  private cachedValue!: T;
  private isDirty = true;
  private isEvaluating = false;
  private subscribers = new Set<Subscriber>();
  private dependencies = new Set<Dependency>();

  constructor(fn: () => T) {
    this.fn = fn;
  }

  addDependency(dep: Dependency): void {
    this.dependencies.add(dep);
  }

  removeSubscriber(sub: Subscriber): void {
    this.subscribers.delete(sub);
  }

  markDirty(): void {
    if (!this.isDirty) {
      this.isDirty = true;
      for (const sub of this.subscribers) {
        sub.markDirty();
      }
    }
  }

  run(): void {
    // Computed оновлюється ліниво при get(), але сповіщає своїх підписників
    for (const sub of Array.from(this.subscribers)) {
      if (batchDepth > 0) {
        pendingEffects.add(sub);
      } else {
        sub.run();
      }
    }
  }

  get(): T {
    if (this.isEvaluating) {
      throw new Error("Виявлено циклічну залежність у графі обчислень!");
    }

    if (activeSubscriber) {
      this.subscribers.add(activeSubscriber);
      activeSubscriber.addDependency(this);
    }

    if (this.isDirty) {
      // Очищаємо старі залежності перед новим виконанням формули
      for (const dep of this.dependencies) {
        dep.removeSubscriber(this);
      }
      this.dependencies.clear();

      this.isEvaluating = true;
      pushContext(this);
      try {
        const newValue = this.fn();
        this.cachedValue = newValue;
        this.isDirty = false;
      } finally {
        popContext();
        this.isEvaluating = false;
      }
    }

    return this.cachedValue;
  }
}

export function createComputed<T>(fn: () => T): () => T {
  const c = new Computed(fn);
  return () => c.get();
}

// ── 3. Effect (Кінцевий споживач / Ефект) ─────────────────────────────────────
export class Effect implements Subscriber {
  private fn: () => void;
  private isDirty = true;
  private isRunning = false;
  private dependencies = new Set<Dependency>();

  constructor(fn: () => void) {
    this.fn = fn;
    this.run();
  }

  addDependency(dep: Dependency): void {
    this.dependencies.add(dep);
  }

  markDirty(): void {
    this.isDirty = true;
  }

  run(): void {
    if (!this.isDirty || this.isRunning) return;

    // Очищаємо підписки попереднього запуску
    for (const dep of this.dependencies) {
      dep.removeSubscriber(this);
    }
    this.dependencies.clear();

    this.isDirty = false;
    this.isRunning = true;
    pushContext(this);
    try {
      this.fn();
    } finally {
      popContext();
      this.isRunning = false;
    }
  }

  dispose(): void {
    for (const dep of this.dependencies) {
      dep.removeSubscriber(this);
    }
    this.dependencies.clear();
  }
}

export function createEffect(fn: () => void): () => void {
  const e = new Effect(fn);
  return () => e.dispose();
}

// ── Демонстрація перевірки на відсутність глітчів ────────────────────────────
const [a, setA] = createSignal(1);

const b = createComputed(() => {
  const v = a();
  console.log(`  [Обчислення B] a + 1 = ${v + 1}`);
  return v + 1;
});

const c = createComputed(() => {
  const v = a();
  console.log(`  [Обчислення C] a * 2 = ${v * 2}`);
  return v * 2;
});

const d = createComputed(() => {
  const bVal = b();
  const cVal = c();
  console.log(`  [Обчислення D] B(${bVal}) + C(${cVal}) = ${bVal + cVal}`);
  return bVal + cVal;
});

console.log("=== Початкове створення Effect ===");
createEffect(() => {
  console.log(`-> ГОЛОВНИЙ РЕЗУЛЬТАТ D = ${d()}`);
});

console.log("\n=== Зміна a: 1 -> 2 (без глітчів) ===");
setA(2);

console.log("\n=== Пакетна зміна (batch) ===");
batch(() => {
  setA(3);
  setA(5);
});
