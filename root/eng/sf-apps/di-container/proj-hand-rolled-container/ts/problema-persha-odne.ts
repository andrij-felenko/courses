resolve<T>(promise: Ctor<T>): T {
  // 0. чи вже є готовий? одинак — віддати збережене, не будувати вдруге
  if (this.cache.has(promise)) return this.cache.get(promise) as T;

  const rec = this.bindings.get(promise) ?? { impl: promise, deps: [] };
  const args = rec.deps.map((dep) => this.resolve(dep));

  const obj = new rec.impl(...args) as T;
  this.cache.set(promise, obj);     // запам'ятати — наступний раз повернемо цей самий
  return obj;
}
