const BASE = "https://api.dh.io/errors";
const CT = "application/problem+json";

interface Problem { status: number; headers: Record<string, string>; body: Record<string, unknown>; }

// detail — АВТОРСЬКИЙ текст на випадок, ніколи не String(err):
// сире err.message могло б винести назовні нутрощі нижнього шару.
function detailFor(err: DomainError): string {
  if (err instanceof DeviceNotFound)    return `Пристрою ${err.id} немає або він не ваш.`;
  if (err instanceof DeviceUnavailable) return "Давач не відповідає, спробуйте за кілька секунд.";
  if (err instanceof InvalidCommand)    return `Поле «${err.field}»: ${err.reason}.`;
  if (err instanceof RateLimited)       return "Забагато запитів, зачекайте перед повтором.";
  return "Помилка.";
}

function toProblem(err: unknown, reqId: string, opts = { exposeInternals: false }): Problem {
  const row = err instanceof Error ? CATALOG.get(err.constructor) : undefined;

  if (row && err instanceof DomainError) {
    const headers: Record<string, string> = { "Content-Type": CT };
    const body: Record<string, unknown> = {
      type: `${BASE}/${row.code.replace(/_/g, "-")}`,   // device_not_found → …/device-not-found
      title: row.title,
      status: row.status,
      code: row.code,                                   // машинний ярлик
      detail: detailFor(err),                           // людський текст
      requestId: reqId,                                 // кореляційний id — той самий, що в журналі
    };
    if (row.retryable) {
      body.retryable = true;
      // фіксована пауза — з рядка; динамічна (ліміт) — із самого винятку
      const ra = err instanceof RateLimited ? err.retryAfterS : row.retryAfterS;
      if (ra !== undefined) headers["Retry-After"] = String(ra);
    }
    if (err instanceof InvalidCommand) body.field = err.field; // яке поле не так
    return { status: row.status, headers, body };
  }

  // ── гілка «усе інше»: це БАГ, а не факт світу ──
  log.error({ reqId, err });                            // лог РАЗ, саме тут, зі стеком — ВДОМА
  const body: Record<string, unknown> = {
    type: "about:blank",                                // «нічого понад статус» (RFC 9457 §4.2.1)
    title: "Внутрішня помилка",
    status: 500,
    code: "internal",
    detail: "Сталася непередбачена помилка.",
    requestId: reqId,
  };
  if (opts.exposeInternals) body.debug = String(err instanceof Error ? err.stack : err); // ЛИШЕ dev
  return { status: 500, headers: { "Content-Type": CT }, body };
}
