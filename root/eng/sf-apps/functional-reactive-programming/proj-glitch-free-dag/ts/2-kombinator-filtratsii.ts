export function filter<T>(source: () => T, predicate: (val: T) => boolean, initial: T): () => T {
  let lastValid = initial;
  return createComputed(() => {
    const val = source();
    if (predicate(val)) {
      lastValid = val;
    }
    return lastValid;
  });
}
