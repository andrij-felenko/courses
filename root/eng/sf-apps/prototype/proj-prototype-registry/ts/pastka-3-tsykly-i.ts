function deepClone<T>(value: T, memo = new Map<object, any>()): T {
  if (value === null || typeof value !== "object") return value;  // примітив — як є
  if (memo.has(value)) return memo.get(value);   // вже копіювали — ТА САМА копія

  // зберегти клас: копія має той самий прототип, що й оригінал
  const copy = Array.isArray(value)
    ? [] as any
    : Object.create(Object.getPrototypeOf(value));

  memo.set(value, copy);                          // ← реєстрація ДО рекурсії рве цикл
  for (const k of Object.keys(value))
    copy[k] = deepClone((value as any)[k], memo);
  return copy;
}
