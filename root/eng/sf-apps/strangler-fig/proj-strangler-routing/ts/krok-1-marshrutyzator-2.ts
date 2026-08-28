// Виклики в старе й нове — заглушки під реальний HTTP-клієнт вашого шлюзу.
declare function callLegacy(req: Request): Promise<Response>;   // старий моноліт
declare function callService(base: string, req: Request): Promise<Response>;

// Стабільний ключ клієнта: беремо id користувача зі шляху /api/users/:id.
// У житті це частіше id із токена автентифікації, а не з URL.
function userKeyOf(path: string): string {
  const m = path.match(/\/api\/users\/([^/]+)/);
  return m ? m[1] : "anon";
}

async function intercept(rules: RouteRule[], req: Request): Promise<Response> {
  const path = new URL(req.url).pathname;
  const rule = rules.find(r => r.pattern.test(path));
  if (!rule) return callLegacy(req);          // ніхто цей шлях не переносив

  const key = userKeyOf(path);

  if (goesToService(rule, key)) {
    // основний потік цього клієнта — у новий сервіс
    return callService(rule.serviceUrl, req);
  }
  // основний потік — у старе (тут згодом стане тіньова звірка для читань)
  return callLegacy(req);
}
