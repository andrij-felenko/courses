type Ctor<T = any> = new (...args: any[]) => T;

class Container {
  private bindings = new Map<Ctor, { impl: Ctor; deps: Ctor[] }>();

  bind<T>(promise: Ctor<T>, impl: Ctor<T>, deps: Ctor[] = []): this {
    this.bindings.set(promise, { impl, deps });
    return this;
  }

  resolve<T>(promise: Ctor<T>): T {
    // 1. яку реалізацію будувати (нема прив'язки — сам тип, без залежностей)
    const rec = this.bindings.get(promise) ?? { impl: promise, deps: [] };

    // 2+3. deps ми оголосили заздалегідь — рекурсивно збираємо кожну
    const args = rec.deps.map((dep) => this.resolve(dep));

    // 4. усі залежності в руках — покликати конструктор
    return new rec.impl(...args) as T;
  }
}
