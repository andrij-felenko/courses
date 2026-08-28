// Який щабель драбини віддав відповідь — рівно ці чотири.
type Rung = "live" | "cache" | "default" | "unavailable";

// Те, що обгортка ЗАВЖДИ повертає: значення, щабель і чи воно застаріле.
interface Served<T> {
  value: T;
  rung: Rung;
  stale: boolean;
}

interface Entry<T> { value: T; at: number; } // тепла копія з відміткою часу
interface Cache<T> {
  get(key: string): Entry<T> | undefined;
  put(key: string, value: T): void;
}

// Policy — це драбина В ДАНИХ: які щаблі ввімкнені саме для ЦЬОГО виклику.
interface Policy<T> {
  op: string;                      // ім'я для метрик: "readState", "canCommand:unlock"
  cache: Cache<T> | null;          // null → щабель кешу вимкнено (напр., для ґейта)
  staleBudgetMs: number;           // кеш віддаємо, лише поки вік ≤ цього
  smartDefault: (() => T) | null;  // null → дефолту нема; для ґейта це fail-open/closed
}
