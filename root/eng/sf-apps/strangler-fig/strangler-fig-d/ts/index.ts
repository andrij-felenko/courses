// Перехоплювач: поки що прозорий — усі шляхи ведуть у старий моноліт.
type Handler = (req: Request) => Promise<Response>;

const legacy: Handler = (req) => callMonolith(req);   // старий застосунок
const routes: Array<[RegExp, Handler]> = [
  // порожньо: жодну можливість ще не перенесено
];

async function intercept(req: Request): Promise<Response> {
  const path = new URL(req.url).pathname;
  for (const [pattern, handler] of routes) {
    if (pattern.test(path)) return handler(req);   // є новий маршрут — туди
  }
  return legacy(req);                              // немає — у старе, як завжди
}
