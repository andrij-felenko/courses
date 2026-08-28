// Чесний мінімум: тільки читання. Це вміють УСІ списки.
interface ReadableList<T> {
  get(i: number): T;
  size(): number;
}

// Розширення: додавання — окрема обіцянка, лише для тих, хто вміє.
interface MutableList<T> extends ReadableList<T> {
  add(x: T): void;
}

// Змінний список реалізує ОБИДВА інтерфейси.
class ArrayList<T> implements MutableList<T> {
  private items: T[] = [];
  get(i: number): T { return this.items[i]; }
  size(): number { return this.items.length; }
  add(x: T): void { this.items.push(x); }
}

// Незмінний реалізує ЛИШЕ ReadableList — про add навіть не згадує.
class ImmutableList<T> implements ReadableList<T> {
  private readonly items: readonly T[];
  constructor(initial: readonly T[]) { this.items = [...initial]; }
  get(i: number): T { return this.items[i]; }
  size(): number { return this.items.length; }
}
