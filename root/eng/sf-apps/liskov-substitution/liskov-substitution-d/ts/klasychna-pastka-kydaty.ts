class List<T> {
  protected items: T[] = [];
  get(i: number): T { return this.items[i]; }
  add(x: T): void { this.items.push(x); }
}

// «Незмінний список — це ж різновид списка?» — і тут пастка:
class ImmutableList<T> extends List<T> {
  add(_x: T): void {
    throw new Error("не можна: список незмінний");   // посилив передумову
  }
}

// Клієнт, написаний чесно під List, ламається:
function fill(list: List<number>): void {
  for (let i = 0; i < 3; i++) list.add(i);   // на ImmutableList — вибух
}
