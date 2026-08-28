type Ctor<T> = new (...args: never[]) => T;
type Pk = string | number;

class IdentityMap {
  // Map порівнює ключі за посиланням, тож кортеж [Order, 42] не спрацює:
  // кожен літерал масиву — новий об'єкт. Тому мапа вкладена: тип → (ключ → об'єкт).
  readonly #byType = new Map<Ctor<unknown>, Map<Pk, unknown>>();

  constructor(private readonly db: Db) {}

  get<T>(cls: Ctor<T>, pk: Pk): T | undefined {
    return this.#byType.get(cls)?.get(pk) as T | undefined;
  }

  add<T extends { pk: Pk }>(cls: Ctor<T>, obj: T): T {
    let bucket = this.#byType.get(cls);
    if (!bucket) this.#byType.set(cls, (bucket = new Map()));
    const existing = bucket.get(obj.pk);
    if (existing !== undefined && existing !== obj) {
      throw new Error(`${cls.name}#${obj.pk} уже в мапі — це двійник`);
    }
    bucket.set(obj.pk, obj);
    return obj;
  }

  async load<T extends { pk: Pk }>(cls: Ctor<T> & { fromRow(r: Row): T }, pk: Pk) {
    const found = this.get(cls, pk);
    if (found !== undefined) return found;     // влучання: до бази не йдемо
    const row = await this.db.selectOne(cls, pk);
    return row ? this.add(cls, cls.fromRow(row)) : undefined;
  }
}
