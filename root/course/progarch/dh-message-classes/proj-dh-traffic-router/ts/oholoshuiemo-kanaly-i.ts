// ПРИМІТИВ 1 — точкова черга.  Суть: кожне повідомлення дістає РІВНО ОДИН споживач.
class Queue<T> {
  private consumers: ((m: T) => void)[] = [];
  private next = 0;                       // ОДИН спільний курсор на всіх споживачів
  subscribe(fn: (m: T) => void): void { this.consumers.push(fn); }
  send(m: T): void {
    if (this.consumers.length === 0) throw new Error("черга без споживача — нікому доправити");
    const i = this.next++ % this.consumers.length;   // наступний за чергою — і лише він
    this.consumers[i](m);
  }
}
