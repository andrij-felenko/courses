type AsyncHandler = (event: unknown) => Promise<void> | void;

class AsyncEventBus {
  private handlers = new Map<string, AsyncHandler[]>();

  subscribe(type: string, handler: AsyncHandler): void {
    const list = this.handlers.get(type) ?? [];
    list.push(handler);
    this.handlers.set(type, list);
  }

  // повертається ОДРАЗУ; обробники йдуть у наступному такті
  publish(type: string, event: unknown): void {
    const handlers = this.handlers.get(type) ?? [];
    queueMicrotask(async () => {
      for (const handler of handlers) {
        try {
          await handler(event);            // збій одного не валить видавця…
        } catch (err) {
          console.error(`handler for ${type} failed`, err);   // …ловимо тут
        }
      }
    });
  }
}
