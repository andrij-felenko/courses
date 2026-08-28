async function intercept(rules: RouteRule[], req: Request): Promise<Response> {
  const path = new URL(req.url).pathname;
  const rule = rules.find(r => r.pattern.test(path));
  if (!rule) return callLegacy(req);

  const isWrite = req.method === "PUT" || req.method === "POST"
               || req.method === "PATCH" || req.method === "DELETE";

  if (isWrite) {
    // запис іде туди, де ЗАРАЗ власник даних; друга база наздоганяє через outbox
    // (напрям власності задає той самий rule.target — тож теж оборотний конфігом)
    return rule.target === "service"
      ? callService(rule.serviceUrl, req)   // власник — новий сервіс
      : callLegacy(req);                    // власник — моноліт
  }

  // читання: стабільний canary + тіньова звірка
  if (goesToService(rule, userKeyOf(path))) {
    return callService(rule.serviceUrl, req);   // цей клієнт уже на новому
  }
  return readWithShadow(rule, req);             // старе клієнту, нове тіньово
}
