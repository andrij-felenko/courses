interface ReadableList<T> {          // чесний мінімум: тільки читання
  get(i: number): T;
  size(): number;
}

interface MutableList<T> extends ReadableList<T> {
  add(x: T): void;                   // додавання — окрема, ширша обіцянка
}

// Тепер fill вимагає рівно те, що йому треба, — і Immutable сюди НЕ підставиш:
function fill(list: MutableList<number>): void {
  for (let i = 0; i < 3; i++) list.add(i);
}
