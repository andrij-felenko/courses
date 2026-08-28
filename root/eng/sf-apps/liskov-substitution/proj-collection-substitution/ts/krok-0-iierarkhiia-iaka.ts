class ArrayList<T> {
  protected items: T[] = [];

  get(i: number): T { return this.items[i]; }
  size(): number { return this.items.length; }
  add(x: T): void { this.items.push(x); }
}

// «Незмінний список — різновид списка?» — і тут закладено пастку:
class ImmutableList<T> extends ArrayList<T> {
  constructor(initial: T[]) {
    super();
    this.items = [...initial];        // наповнили раз, при створенні
  }
  add(_x: T): void {
    throw new Error("список незмінний: додавати не можна");
  }
}
