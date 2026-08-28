class Store {
  private queue: Action[] = [];
  private log: Action[] = [];
  private running = false;

  constructor(private state: State, private io: Io) {}

  dispatch(a: Action): void {
    this.queue.push(a);
    if (this.running) return;          // цикл уже крутиться — він забере й цю дію
    this.running = true;

    while (this.queue.length > 0) {
      const cur = this.queue.shift()!;

      this.log.push(cur);                    // журнал: що прийшло і в якому порядку
      const step = update(this.state, cur);  // єдине місце, де народжується стан
      this.state = step.state;
      this.io.paint(view(this.state));       // рівно один кадр на завершену версію

      for (const e of step.effects)          // dispatch звідси лише стає в чергу
        this.perform(e);
    }

    this.running = false;
  }

  private perform(e: Effect): void {
    switch (e.kind) {
      case "запит-курсу": this.io.fetchRate(this);              break;
      case "зберегти":    this.io.persist(this.state);          break;
      case "повторити":   this.io.retryAfter(e.afterMs, this);  break;
    }
  }
}
