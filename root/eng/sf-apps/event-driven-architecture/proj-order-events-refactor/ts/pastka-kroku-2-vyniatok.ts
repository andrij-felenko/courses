// НЕПРАВИЛЬНО: та сама шина, але БЕЗ try/catch
publish(type: string, event: unknown): void {
  const handlers = this.handlers.get(type) ?? [];
  queueMicrotask(async () => {
    for (const handler of handlers) {
      await handler(event);       // впав? виняток стане unhandled rejection
    }                              // — і, якщо його ніхто не слухає, ПРОСТО ЗНИКНЕ
  });
}
// placeOrder давно повернулась. Лист не пішов. У метриках чисто.
// Ніхто не впав, ніхто не залогував. Помилки наче й не було.
