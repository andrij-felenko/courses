type Handler = (event: unknown) => void;

class EventBus {
  private handlers = new Map<string, Handler[]>();

  // підписник заявляє інтерес до типу події
  subscribe(eventType: string, handler: Handler): void {
    const list = this.handlers.get(eventType) ?? [];
    list.push(handler);
    this.handlers.set(eventType, list);
  }

  // видавець оголошує факт; шина розносить його всім підписаним
  publish(eventType: string, event: unknown): void {
    for (const handler of this.handlers.get(eventType) ?? []) {
      handler(event);
    }
  }
}
