// ПРИМІТИВ 4 — робоча черга + пул.  Суть: черга (один таск — один виконавець),
// але виконавців БАГАТО; перший вільний вихоплює наступний таск.
class WorkQueue<T> {
  private buf: T[] = [];
  submit(job: T): void { this.buf.push(job); }
  async drain(workers: number, handle: (job: T, w: number) => Promise<void>): Promise<void> {
    const run = async (id: number) => {
      let job: T | undefined;
      while ((job = this.buf.shift()) !== undefined) {   // shift синхронний — таск дістанеться одному
        await handle(job, id);
      }
    };
    await Promise.all(Array.from({ length: workers }, (_, i) => run(i)));
  }
}
