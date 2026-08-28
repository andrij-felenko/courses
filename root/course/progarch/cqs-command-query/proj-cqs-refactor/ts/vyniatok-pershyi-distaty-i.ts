class CommandQueue<T> {
  private items: T[] = [];

  enqueue(job: T): void { this.items.push(job); }      // КОМАНДА — чиста

  // ВИНЯТОК: дістати-й-вилучити ОДНИМ кроком
  dequeue(): T | undefined {
    return this.items.shift();   // повертає перший і тут-таки прибирає його
  }

  get size(): number { return this.items.length; }     // ЗАПИТ
}
