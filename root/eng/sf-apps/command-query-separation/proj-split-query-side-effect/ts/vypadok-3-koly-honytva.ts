// TS: атомарність будуємо на індивідуальному замку навколо
// неподільної секції (у Node немає вбудованого атомарного лічильника
// для звичайного числа — але ідея та сама: read-modify-write як ОДНЕ ціле).
class ViewCounter {
  private hits = 0;
  private readonly lock = new Mutex();

  // Чесний виняток: І міняє, І повертає — але НЕПОДІЛЬНО.
  async nextViewNumber(): Promise<number> {
    return this.lock.runExclusive(() => {
      this.hits += 1;      // зміна
      return this.hits;    // і повернення — між ними ніхто не влізе
    });
  }
}
