// Map порівнює ключі за посиланням, тож пара (клас, pk) сама по собі ключем
// не стане. Звужуємо її до рядка — через сталий номер класу, а не через
// cls.name: імена класів у різних модулях залюбки збігаються.
const classIds = new WeakMap<EntityClass, number>();
let nextClassId = 0;

function keyOf(obj: Entity): string {
  const cls = obj.constructor as EntityClass;
  let id = classIds.get(cls);
  if (id === undefined) classIds.set(cls, (id = nextClassId++));
  return `${id}:${String(obj.pk)}`;
}

function pick(obj: Entity, names: readonly string[]): Row {
  return Object.fromEntries(names.map((n) => [n, Reflect.get(obj, n)]));
}

class UnitOfWork {
  readonly #new = new Map<string, Entity>();
  readonly #dirty = new Map<string, Entity>();
  readonly #removed = new Map<string, Entity>();
  readonly #fields = new Map<string, Set<string>>();

  registerNew(obj: Entity): void {
    this.#new.set(keyOf(obj), obj);
  }

  registerDirty(obj: Entity, field: string): void {
    const key = keyOf(obj);
    if (this.#new.has(key) || this.#removed.has(key)) return;
    this.#dirty.set(key, obj);
    let fields = this.#fields.get(key);
    if (fields === undefined) this.#fields.set(key, (fields = new Set()));
    fields.add(field);
  }

  registerRemoved(obj: Entity): void {
    const key = keyOf(obj);
    this.#new.delete(key);
    this.#dirty.delete(key);
    this.#fields.delete(key);
    this.#removed.set(key, obj);
  }

  get isEmpty(): boolean {
    return this.#new.size === 0 && this.#dirty.size === 0 && this.#removed.size === 0;
  }

  forget(): void {
    this.#new.clear();
    this.#dirty.clear();
    this.#removed.clear();
    this.#fields.clear();
  }

  commit(db: Db): void {
    for (const obj of this.#new.values()) {
      const cls = obj.constructor as EntityClass;
      db.insert(cls.table, obj.pk, pick(obj, cls.columns));
    }
    for (const [key, obj] of this.#dirty) {
      const cls = obj.constructor as EntityClass;
      // пишемо ЛИШЕ те, що справді змінили, а не всі стовпці підряд
      db.update(cls.table, obj.pk, pick(obj, [...this.#fields.get(key)!].sort()));
    }
    for (const obj of this.#removed.values()) {
      db.delete((obj.constructor as EntityClass).table, obj.pk);
    }
    this.forget();   // записано — відпускаємо: об'єкти знову слабкі
  }
}
