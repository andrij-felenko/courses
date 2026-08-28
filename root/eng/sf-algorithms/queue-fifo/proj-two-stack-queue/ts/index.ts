class Queue<T> {
  #in: T[] = [];               // сюди пхаємо (enqueue)
  #out: T[] = [];              // звідси знімаємо (dequeue / peek)

  enqueue(x: T): void {
    this.#in.push(x);          // просто на вершину вхідного
  }

  #transfer(): void {
    // переливаємо ЛИШЕ коли вихідний порожній
    if (this.#out.length === 0) {
      while (this.#in.length > 0) {
        this.#out.push(this.#in.pop()!);   // друге перевертання
      }
    }
  }

  dequeue(): T {
    this.#transfer();
    if (this.#out.length === 0) throw new Error("черга порожня");
    return this.#out.pop()!;
  }

  peek(): T {
    this.#transfer();          // peek теж змушує переливання
    if (this.#out.length === 0) throw new Error("черга порожня");
    return this.#out[this.#out.length - 1];
  }

  get size(): number {
    return this.#in.length + this.#out.length;
  }
}
