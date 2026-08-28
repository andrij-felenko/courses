class Pool<T> {
  private free: T[];
  private inUse = new Set<T>();

  constructor(private create: () => T, size: number) {
    this.free = Array.from({ length: size }, () => create());  // заплатили за народження наперед
  }

  acquire(): T {
    const obj = this.free.pop() ?? this.create();
    this.inUse.add(obj);
    return obj;
  }

  release(obj: T): void {
    this.inUse.delete(obj);
    this.free.push(obj);              // назад на полицю, НЕ знищуємо
  }
}
