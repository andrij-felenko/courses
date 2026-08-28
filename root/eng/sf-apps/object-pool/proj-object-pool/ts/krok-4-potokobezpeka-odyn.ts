// TS-рантайм — однопотоковий (event loop), «замка» в сенсі потоків нема.
// Але асинхронність дає СВОЮ гонитву: між await-ами вклинюється чужий код.
// Тому пул тут блокує не потік, а обіцянку (Promise): черга тих, хто чекає.
class Pool<T> {
  private free: T[] = [];
  private created = 0;
  private waiters: Array<(obj: T) => void> = [];   // хто чекає вільного

  constructor(
    private factory: () => T,
    private reset: (o: T) => void,
    private max: number,
    private timeoutMs = 5000,
  ) {}

  async acquire(): Promise<T> {
    if (this.free.length > 0) return this.free.pop()!;   // є вільний
    if (this.created < this.max) {                        // можна вирости
      this.created++;
      return this.factory();
    }
    // усе зайнято — стаємо в чергу обіцянок, з таймаутом
    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        const i = this.waiters.indexOf(give);
        if (i >= 0) this.waiters.splice(i, 1);
        reject(new Error("пул вичерпано"));
      }, this.timeoutMs);
      const give = (obj: T) => { clearTimeout(timer); resolve(obj); };
      this.waiters.push(give);
    });
  }

  release(obj: T): void {
    this.reset(obj);
    const give = this.waiters.shift();            // хтось чекає?
    if (give) give(obj);                          // віддати прямо йому
    else this.free.push(obj);                     // ні — на полицю
  }
}
