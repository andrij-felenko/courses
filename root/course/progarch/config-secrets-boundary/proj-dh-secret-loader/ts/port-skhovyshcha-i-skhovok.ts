// ПОРТ: застосунок знає лише «дай значення за іменем». Що по той бік —
// змінна середовища, хмарний вольт, файл, — його не обходить.
interface SecretStore {
  get(name: string): Promise<string>;   // кидає, якщо секрета нема
}

// СХОВОК: справжнє значення — за приватним полем; назовні за замовчуванням ‹secret›.
const REDACTED = "‹secret›";
class Secret {
  readonly #value: string;                    // приватне поле ES2022 — не видно ЖОДНОМУ обходу
  constructor(value: string) { this.#value = value; }

  expose(): string { return this.#value; }    // ЄДИНИЙ навмисний вихід значення

  toString(): string { return REDACTED; }     // рядок / шаблон `${s}`
  toJSON():   string { return REDACTED; }     // JSON.stringify, структурний логер
  [Symbol.for("nodejs.util.inspect.custom")]() { return REDACTED; }  // console.log, util.inspect
}
