// НАЇВНО: get, тоді put. Виглядає правильно. Не є.
class NaiveStore {
  private done = new Map<string, Result>();
  constructor(private execute: (c: Command) => Promise<Result>) {}

  async handle(key: string, cmd: Command): Promise<Result> {
    const seen = this.done.get(key);
    if (seen) return seen;                   // ← читаємо: ключ знайомий?
    const result = await this.execute(cmd);  // ← ...а тут AWAIT — керування йде до конкурента
    this.done.set(key, result);              // ← пишемо, але вже надто пізно
    return result;
  }
}
