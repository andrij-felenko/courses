type Ctor<T> = new (...args: any[]) => T;   // «конструктор, що дає T»

class Container {
  // обіцянка(токен) → { реалізація, її залежності }.
  private bindings = new Map<Ctor, { impl: Ctor; deps: Ctor[] }>();

  bind<T>(promise: Ctor<T>, impl: Ctor<T>, deps: Ctor[] = []): this {
    this.bindings.set(promise, { impl, deps });
    return this;              // щоб зчіплювати: c.bind(...).bind(...)
  }
}
