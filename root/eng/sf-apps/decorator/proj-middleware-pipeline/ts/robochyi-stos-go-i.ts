// Обробник — функція запит→відповідь; middleware — функція, що вертає обробник.
type Req = { method: string; path: string; headers: Record<string, string> };
type Res = { status: number; headers: Record<string, string>; body: string };
type Handler = (req: Req) => Promise<Res>;
type Middleware = (next: Handler) => Handler;

// Logger: «до» — пишемо вхід; делегуємо; «після» — пишемо вихід.
const logger: Middleware = (next) => async (req) => {
  console.log(`→ ${req.method} ${req.path}`);       // ДО делегації
  const res = await next(req);                       // делегація глибше
  console.log(`← ${res.status} ${req.path}`);        // ПІСЛЯ делегації
  return res;
};

// Timer: «до» — засікли старт; делегуємо; «після» — зміряли тривалість.
const timer: Middleware = (next) => async (req) => {
  const start = Date.now();
  const res = await next(req);
  console.log(`⏱ ${req.path} за ${Date.now() - start}ms`);
  return res;
};
