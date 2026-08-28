import type { Request, Response, NextFunction, RequestHandler } from "express";
import { Counter } from "prom-client";

// Один лічильник на весь застосунок. Різні маршрути — це різні ЗНАЧЕННЯ мітки
// route, а не нові метрики.
const deprCalls = new Counter({
  name: "deprecated_route_calls_total",
  help: "Виклики застарілих маршрутів за клієнтом",
  labelNames: ["route", "client"] as const,
});

// ключ API -> людська назва клієнта. Джерело — ваш реєстр інтеграторів.
const KNOWN_CLIENTS = new Map<string, string>([
  ["ak_live_9f3…", "acme-mobile"],
  ["ak_live_2b7…", "partner-erp"],
]);

interface DeprecationOpts {
  route: string;      // логічна назва для мітки, напр. "orders.v1"
  announced: string;  // ISO-дата оголошення, "2024-06-30"
  sunset: string;     // ISO-дата зняття,      "2025-12-31"
  docs: string;       // URL інструкції з переходу
}

export function deprecated(opts: DeprecationOpts): RequestHandler {
  const announcedAt = new Date(`${opts.announced}T00:00:00Z`);
  const sunsetAt = new Date(`${opts.sunset}T23:59:59Z`);

  // Контракт перевіряємо ДО старту: зняття не може бути раніше за оголошення.
  if (!(sunsetAt > announcedAt)) {
    throw new Error(
      `deprecated(${opts.route}): sunset ${opts.sunset} не пізніше за announced ${opts.announced}`,
    );
  }

  // Форматуємо ОДИН раз. Два різні формати — не помилка, а вимога стандартів:
  //   Deprecation — Structured Field Date: '@' + секунди Unix   (RFC 9745)
  //   Sunset      — HTTP-date у GMT, англійські назви днів/міс.  (RFC 8594)
  const deprValue = `@${Math.floor(announcedAt.getTime() / 1000)}`;
  const sunsetValue = sunsetAt.toUTCString();  // "Wed, 31 Dec 2025 23:59:59 GMT"
  const linkValue = `<${opts.docs}>; rel="deprecation"; type="text/html"`;

  return (req: Request, res: Response, next: NextFunction) => {
    res.setHeader("Deprecation", deprValue);
    res.setHeader("Sunset", sunsetValue);
    res.setHeader("Link", linkValue);
    deprCalls.inc({ route: opts.route, client: clientId(req) });
    next();
  };
}

// Обмежена кардинальність: відома назва або єдина мітка "unknown".
function clientId(req: Request): string {
  const key = req.header("x-api-key") ?? "";
  return KNOWN_CLIENTS.get(key) ?? "unknown";
}

// вмикається на ОДИН маршрут, не на весь застосунок:
app.get("/v1/orders",
  deprecated({ route: "orders.v1", announced: "2024-06-30", sunset: "2025-12-31", docs: DOCS }),
  listOrdersV1);
