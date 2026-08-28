// доменні помилки — ті самі, що впираються в межу HTTP знизу
abstract class DomainError extends Error {}
class DeviceNotFound    extends DomainError { constructor(public id: string) { super("device not found"); } }
class DeviceUnavailable extends DomainError { constructor(public id: string) { super("device offline"); } }
class InvalidCommand    extends DomainError { constructor(public field: string, public reason: string) { super("invalid command"); } }
class RateLimited       extends DomainError { constructor(public retryAfterS: number) { super("rate limited"); } }

// рядок каталогу = контракт ОДНОГО класу, як дані
interface Row {
  status: number;      // HTTP-статус
  code: string;        // стабільний машинний ярлик — НЕ міняється ніколи
  title: string;       // короткий людський заголовок (RFC 9457 title)
  retryable?: boolean; // чи має сенс повторювати
  retryAfterS?: number;// фіксована пауза, коли вона стала для класу
}

// КЛЮЧ — сам клас (посилання на конструктор), а не рядок-назва:
// стійке до мініфікації, яка перейменувала б err.name.
const CATALOG = new Map<Function, Row>([
  [DeviceNotFound,    { status: 404, code: "device_not_found"   , title: "Пристрій не знайдено" }],
  [DeviceUnavailable, { status: 503, code: "device_unavailable" , title: "Пристрій тимчасово недоступний", retryable: true, retryAfterS: 5 }],
  [InvalidCommand,    { status: 400, code: "invalid_command"    , title: "Некоректна команда" }],
  [RateLimited,       { status: 429, code: "rate_limited"       , title: "Забагато запитів", retryable: true }],
]);
