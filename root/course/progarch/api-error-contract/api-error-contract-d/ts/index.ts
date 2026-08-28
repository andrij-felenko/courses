// доменні помилки — ті самі, що підіймалися крізь шари; тут вони впираються в межу HTTP
class DeviceNotFound   extends Error { constructor(public id: string) { super("no device"); } }
class DeviceUnavailable extends Error { constructor(public id: string) { super("offline"); } }

// одне місце перекладу: доменна помилка → HTTP-відповідь як контракт
function toProblem(err: unknown, reqId: string) {
  if (err instanceof DeviceNotFound)
    return { status: 404, headers: {},
      body: { type: "https://api.dh.io/errors/device-not-found",
              title: "Пристрій не знайдено", status: 404,
              code: "device_not_found", detail: `Пристрою ${err.id} немає.`,
              requestId: reqId } };

  if (err instanceof DeviceUnavailable)
    return { status: 503, headers: { "Retry-After": "5" },
      body: { type: "https://api.dh.io/errors/device-unavailable",
              title: "Пристрій тимчасово недоступний", status: 503,
              code: "device_unavailable", retryable: true,
              detail: "Давач не відповідає, спробуйте за кілька секунд.",
              requestId: reqId } };

  // усе інше — це БАГ, а не факт світу: назовні нічого, у журнал — усе
  log.error({ reqId, err });                       // лог РАЗ, саме тут, зі стеком
  return { status: 500, headers: {},
    body: { type: "about:blank", title: "Внутрішня помилка", status: 500,
            code: "internal", detail: "Сталася непередбачена помилка.",
            requestId: reqId } };                   // жодного стека, жодного SQL назовні
}
