type Ctor<T = any> = new (...args: any[]) => T;

class Container {
  private bindings = new Map<Ctor, { impl: Ctor; deps: Ctor[] }>();
  private cache = new Map<Ctor, unknown>();
  private building: Ctor[] = [];             // стек тих, хто ЗАРАЗ будується

  bind<T>(promise: Ctor<T>, impl: Ctor<T>, deps: Ctor[] = []): this {
    this.bindings.set(promise, { impl, deps });
    return this;
  }

  resolve<T>(promise: Ctor<T>): T {
    // кеш: уже зібраний одинак — віддати
    if (this.cache.has(promise)) return this.cache.get(promise) as T;

    // цикл: цей тип уже будується вище по стеку
    if (this.building.includes(promise)) {
      const chain = [...this.building, promise].map((t) => t.name).join(" → ");
      throw new Error(`Циклічна залежність: ${chain}`);
    }

    this.building.push(promise);             // поклали на стек: почали будувати
    let obj: T;
    try {
      const rec = this.bindings.get(promise) ?? { impl: promise, deps: [] };
      const args = rec.deps.map((dep) => this.resolve(dep));   // ← рекурсія: обхід графа
      obj = new rec.impl(...args) as T;
    } finally {
      this.building.pop();                   // зняли зі стека хоч би що
    }

    this.cache.set(promise, obj);            // запам'ятали одинак
    return obj as T;
  }
}
