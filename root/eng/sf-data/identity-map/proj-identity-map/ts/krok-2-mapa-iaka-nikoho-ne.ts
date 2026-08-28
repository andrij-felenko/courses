class IdentityMap {
  protected readonly byType = new Map<EntityClass, Map<Pk, WeakRef<Entity>>>();

  // WeakRef порожньої комірки за собою не прибирає — це робить реєстр
  // фіналізації. Тримане значення — тільки (клас, ключ): якби воно
  // посилалося на сам об'єкт, той не помер би ніколи.
  readonly #sweeper = new FinalizationRegistry<{ cls: EntityClass; pk: Pk }>(({ cls, pk }) => {
    const bucket = this.byType.get(cls);
    // об'єкт міг відродитися під тим самим ключем — тоді комірка вже не наша
    if (bucket !== undefined && bucket.get(pk)?.deref() === undefined) bucket.delete(pk);
  });

  get<T extends Entity>(cls: EntityClass, pk: Pk): T | undefined {
    const bucket = this.byType.get(cls);
    const ref = bucket?.get(pk);
    if (ref === undefined) return undefined;
    const obj = ref.deref();
    if (obj === undefined) bucket!.delete(pk);   // надгробок: реєстр іще не дійшов
    return obj as T | undefined;
  }

  add<T extends Entity>(obj: T): T {
    const cls = obj.constructor as EntityClass;
    let bucket = this.byType.get(cls);
    if (bucket === undefined) this.byType.set(cls, (bucket = new Map()));
    const existing = bucket.get(obj.pk)?.deref();
    if (existing !== undefined && existing !== obj) {
      throw new Error(`(${cls.name}, ${String(obj.pk)}) уже в мапі — це двійник`);
    }
    bucket.set(obj.pk, new WeakRef(obj));
    this.#sweeper.register(obj, { cls, pk: obj.pk });
    return obj;
  }

  values(): Entity[] {
    const live: Entity[] = [];
    for (const bucket of this.byType.values()) {
      for (const ref of bucket.values()) {
        const obj = ref.deref();
        if (obj !== undefined) live.push(obj);
      }
    }
    return live;
  }

  clear(): void {
    this.byType.clear();
  }
  get size(): number {
    return this.values().length;
  }
}
