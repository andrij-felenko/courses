type Ctor = new (...a: never[]) => object;

class UnitOfWork {
  private newObjects: object[] = [];
  private dirty: object[] = [];
  private removed: object[] = [];

  constructor(
    private readonly tx: Transaction,          // одна транзакція на весь блок
    private readonly mappers: Map<Ctor, Mapper>,
  ) {}

  registerNew(o: object): void { this.newObjects.push(o); }        // вставити

  registerDirty(o: object): void {                                 // оновити
    if (!this.dirty.includes(o) && !this.newObjects.includes(o)) this.dirty.push(o);
  }

  registerRemoved(o: object): void {                               // видалити
    const i = this.newObjects.indexOf(o);
    if (i >= 0) { this.newObjects.splice(i, 1); return; }          // народжене й убите — пропустити
    if (!this.removed.includes(o)) this.removed.push(o);
  }

  async commit(): Promise<void> {
    try {
      for (const o of this.newObjects) await this.mapperFor(o).insert(o, this.tx);
      for (const o of this.dirty)      await this.mapperFor(o).update(o, this.tx);
      for (const o of this.removed)    await this.mapperFor(o).delete(o, this.tx);
      await this.tx.commit();                  // усе або нічого
    } catch (e) {
      await this.tx.rollback();
      throw e;
    }
  }

  private mapperFor(o: object): Mapper {
    return this.mappers.get(o.constructor as Ctor)!;
  }
}
