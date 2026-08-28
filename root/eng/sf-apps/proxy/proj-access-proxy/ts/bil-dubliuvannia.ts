// JavaScript/TypeScript: об'єкт Proxy з пастками (trap) get + apply.
// get віддає загорнутий метод; тонкість — прив'язати this до РЕАЛЬНОГО об'єкта.
function loggingProxy<T extends object>(real: T): T {
  return new Proxy(real, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== "function") return value;   // поле — як є
      return function (this: unknown, ...args: unknown[]) {   // ← єдина точка
        log(`→ ${String(prop)}(${args})`);
        const result = Reflect.apply(value, target, args);    // this = target, НЕ проксі!
        log(`← ${String(prop)} = ${result}`);
        return result;
      };
    },
  });
}

// Один проксі накриває весь інтерфейс:
const service: OrderService = loggingProxy(new RealOrderService());
service.getOrder("ord-42");   // trap get("getOrder") → обгортка → лог + делегування
service.placeOrder(order);    // той самий шлях, окремого коду під метод немає
