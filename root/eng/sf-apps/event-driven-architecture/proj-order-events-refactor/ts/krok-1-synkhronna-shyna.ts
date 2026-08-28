type Handler = (event: unknown) => void;

class EventBus {
  private handlers = new Map<string, Handler[]>();

  subscribe(type: string, handler: Handler): void {
    const list = this.handlers.get(type) ?? [];
    list.push(handler);
    this.handlers.set(type, list);
  }

  // викликає обробників ЗАРАЗ ЖЕ, у тому самому потоці
  publish(type: string, event: unknown): void {
    for (const handler of this.handlers.get(type) ?? []) {
      handler(event);
    }
  }
}
