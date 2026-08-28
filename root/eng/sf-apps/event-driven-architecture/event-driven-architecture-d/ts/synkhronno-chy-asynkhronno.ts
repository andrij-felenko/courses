class AsyncEventBus {
  private handlers = new Map<string, ((e: unknown) => Promise<void> | void)[]>();

  subscribe(type: string, h: (e: unknown) => Promise<void> | void): void {
    const list = this.handlers.get(type) ?? [];
    list.push(h);
    this.handlers.set(type, list);
  }

  // повертається ОДРАЗУ; обробники йдуть у наступному такті циклу подій
  publish(type: string, event: unknown): void {
    const handlers = this.handlers.get(type) ?? [];
    queueMicrotask(async () => {
      for (const h of handlers) {
        try {
          await h(event);            // падіння одного не валить видавця…
        } catch (err) {
          console.error(`handler for ${type} failed`, err);  // …його ловлять тут
        }
      }
    });
  }
}
