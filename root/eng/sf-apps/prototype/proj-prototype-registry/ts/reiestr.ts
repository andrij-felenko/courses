class PrototypeRegistry<T extends { clone(): T }> {
  private prototypes = new Map<string, T>();

  register(key: string, proto: T): void {   // покласти зразок під ключем
    this.prototypes.set(key, proto);
  }

  create(key: string): T {
    const proto = this.prototypes.get(key);
    if (!proto) throw new Error(`немає прототипу: ${key}`);
    return proto.clone();                    // новий об'єкт — копія зразка
  }
}
