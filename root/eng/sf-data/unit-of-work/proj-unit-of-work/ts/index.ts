type Ctor<T = object> = new (...a: never[]) => T;

interface Mapper<T = { id: number | null }> {
  entity: Ctor<T>;
  dependsOn: Ctor[];                                    // на які типи вказує ФК
  load(id: number, tx: Tx): Promise<T | null>;
  insert(o: T, tx: Tx): Promise<void>;                  // має заповнити o.id
  update(o: T, tx: Tx): Promise<void>;
  delete(o: T, tx: Tx): Promise<void>;
  fields(o: T): Record<string, unknown>;
}

class UnitOfWork {
  readonly #mappers = new Map<Ctor, Mapper>();
  readonly #identity = new Map<string, { id: number | null }>();   // "Тип#ключ" → об'єкт
  readonly #snapshots = new Map<object, string>();                 // об'єкт → знімок (серіалізований)
  readonly #tracked: object[] = [];                               // порядок обходу знімків
  #new: { id: number | null }[] = [];
  #removed: { id: number | null }[] = [];

  constructor(private readonly tx: Tx, mappers: Mapper[]) {
    for (const m of mappers) this.#mappers.set(m.entity, m);
  }

  // ── завантаження: карта + знімок в одну мить ──
  async read<T extends { id: number | null }>(cls: Ctor<T>, id: number): Promise<T | null> {
    const key = `${cls.name}#${id}`;
    if (this.#identity.has(key)) return this.#identity.get(key) as T;
    const obj = await this.#mappers.get(cls)!.load(id, this.tx) as T | null;
    if (!obj) return null;
    this.#identity.set(key, obj);
    this.#snapshot(obj);
    return obj;
  }

  registerNew(o: { id: number | null }): void { this.#new.push(o); }
  registerRemoved(o: { id: number | null }): void {
    const i = this.#new.indexOf(o);
    if (i >= 0) { this.#new.splice(i, 1); return; }     // народжене й убите — пропустити
    if (!this.#removed.includes(o)) this.#removed.push(o);
  }

  #mapperOf(o: object): Mapper { return this.#mappers.get(o.constructor as Ctor)!; }
  #snapshot(o: object): void {
    this.#snapshots.set(o, JSON.stringify(this.#mapperOf(o).fields(o)));
    if (!this.#tracked.includes(o)) this.#tracked.push(o);
  }

  // ── автовідстеження: хто розійшовся зі знімком ──
  #dirty(): object[] {
    return this.#tracked.filter(o =>
      !this.#removed.includes(o as { id: number | null }) &&
      JSON.stringify(this.#mapperOf(o).fields(o)) !== this.#snapshots.get(o));
  }

  // ── топосорт: батько перед дитиною ──
  #toposort<T extends object>(objs: T[]): T[] {
    const order: Ctor[] = [], seen = new Set<Ctor>();
    const visit = (t: Ctor) => {
      if (seen.has(t)) return;
      seen.add(t);
      for (const p of this.#mappers.get(t)!.dependsOn) visit(p);
      order.push(t);
    };
    for (const o of objs) visit(o.constructor as Ctor);
    const rank = new Map(order.map((t, i) => [t, i] as const));
    return [...objs].sort((a, b) =>
      rank.get(a.constructor as Ctor)! - rank.get(b.constructor as Ctor)!);
  }

  // ── злив: SQL у транзакцію, але транзакція ще жива ──
  async flush(): Promise<void> {
    const dirty = this.#dirty();                        // порахувати ДО вставок
    for (const o of this.#toposort(this.#new)) {        // згори вниз
      await this.#mapperOf(o).insert(o, this.tx);       // призначає o.id
      this.#identity.set(`${o.constructor.name}#${(o as { id: number }).id}`, o as { id: number });
      this.#snapshot(o);
    }
    for (const o of dirty) { await this.#mapperOf(o).update(o, this.tx); this.#snapshot(o); }
    for (const o of this.#toposort(this.#removed).reverse()) {   // знизу вгору
      await this.#mapperOf(o).delete(o, this.tx);
      this.#identity.delete(`${o.constructor.name}#${(o as { id: number }).id}`);
      this.#snapshots.delete(o);
    }
    this.#new = []; this.#removed = [];
  }

  async commit(): Promise<void> {
    try { await this.flush(); await this.tx.commit(); }
    catch (e) { await this.tx.rollback(); throw e; }
  }
}
