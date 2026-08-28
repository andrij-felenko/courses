class Session {
  readonly identityMap: IdentityMap;
  readonly #db: Db;
  readonly #uow = new UnitOfWork();
  #closed = false;

  constructor(db: Db, mapFactory: () => IdentityMap = () => new IdentityMap()) {
    this.#db = db;
    this.identityMap = mapFactory();
  }

  load<T extends Entity>(cls: EntityClass & { fromRow(r: Row): T }, pk: Pk): T | undefined {
    this.#checkOpen();
    const found = this.identityMap.get<T>(cls, pk);
    if (found !== undefined) return found;    // влучання: ні SELECT, ні нового об'єкта
    const row = this.#db.selectOne(cls.table, pk);
    return row === undefined ? undefined : this.#attach(cls.fromRow(row));
  }

  add<T extends Entity>(raw: T): T {
    this.#checkOpen();
    const obj = this.#attach(raw);
    this.#uow.registerNew(obj);
    return obj;
  }

  delete(obj: Entity): void {
    this.#checkOpen();
    this.#uow.registerRemoved(obj);
  }

  #attach<T extends Entity>(raw: T): T {
    const obj = track(raw, this);   // спершу проксі…
    this.identityMap.add(obj);      // …і в мапу лягає ТІЛЬКИ він
    obj.session = this;
    return obj;
  }

  markDirty(obj: Entity, field: string): void {
    if (!this.#closed) this.#uow.registerDirty(obj, field);
  }

  commit(): void {
    this.#checkOpen();
    this.#uow.commit(this.#db);
  }

  rollback(): void {
    this.#uow.forget();
    this.identityMap.clear();       // відкат — стан у пам'яті вже несправжній
  }

  close(): void {
    if (this.#closed) return;
    if (!this.#uow.isEmpty) {
      // мовчки загубити зміни — це рівно та хвороба, яку ми лікуємо
      throw new Error("сесію закривають із незаписаними змінами");
    }
    for (const obj of this.identityMap.values()) obj.session = null;
    this.identityMap.clear();
    this.#closed = true;
  }

  #checkOpen(): void {
    if (this.#closed) throw new Error("сесія закрита");
  }

  // JS не має `with`, тож межу задає функція: тіло всередині, кінець — гарантовано
  static run<T>(db: Db, mapFactory: () => IdentityMap, body: (s: Session) => T): T {
    const s = new Session(db, mapFactory);
    try {
      const result = body(s);
      s.commit();
      return result;
    } catch (e) {
      s.rollback();
      throw e;
    } finally {
      s.close();
    }
  }
}
