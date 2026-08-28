type Lifetime = "singleton" | "scoped" | "transient";
type Factory<T> = (scope: Scope) => T;

class Root {
  private recipes = new Map<Token<unknown>, { life: Lifetime; make: Factory<unknown> }>();
  private singletons = new Map<Token<unknown>, unknown>();   // спільний кеш — на КОРЕНІ
  private frozen = false;

  register<T>(token: Token<T>, life: Lifetime, make: Factory<T>): void {
    if (this.frozen) throw new Error("Реєстрація лише до заморозки кореня");
    this.recipes.set(token, { life, make });
  }
  freeze(): void { this.frozen = true; }

  recipe(token: Token<unknown>) {
    const r = this.recipes.get(token);
    if (!r) throw new Error(`Не зареєстровано: ${token.description}`);
    return r;
  }
  singleton<T>(token: Token<T>, scope: Scope): T {
    if (!this.singletons.has(token)) this.singletons.set(token, this.recipe(token).make(scope));
    return this.singletons.get(token) as T;
  }
  createScope(): Scope { return new Scope(this); }
}

class Scope {
  private cache = new Map<Token<unknown>, unknown>();   // scoped-кеш — свій на КОЖНУ область
  constructor(private root: Root) {}

  resolve<T>(token: Token<T>): T {
    const { life, make } = this.root.recipe(token);
    if (life === "singleton") return this.root.singleton(token, this);
    if (life === "transient") return make(this) as T;    // новий щоразу
    if (!this.cache.has(token)) this.cache.set(token, make(this));  // scoped: один на цю область
    return this.cache.get(token) as T;
  }
}
