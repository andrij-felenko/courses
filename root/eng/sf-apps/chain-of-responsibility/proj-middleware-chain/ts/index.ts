type Ctx = {
  method: string; path: string; ip: string;
  token?: string; user?: string;
  status: number; body: string;
};
type Next = () => Promise<void>;
type Middleware = (ctx: Ctx, next: Next) => Promise<void>;

// Складання: список ланок → одна функція. Робимо це РАЗ, на старті.
function compose(chain: Middleware[]): (ctx: Ctx) => Promise<void> {
  return function run(ctx: Ctx): Promise<void> {
    let lastCalled = -1;                       // лічильник ЦЬОГО запиту, не спільний
    function dispatch(i: number): Promise<void> {
      if (i <= lastCalled) return Promise.reject(new Error('next() покликано двічі'));
      lastCalled = i;
      const fn = chain[i];
      if (!fn) return Promise.resolve();       // дно: next() найглибшої ланки — це «нічого»
      return fn(ctx, () => dispatch(i + 1));
    }
    return dispatch(0);
  };
}

const logger: Middleware = async (ctx, next) => {
  const t0 = performance.now();               // монотонний годинник, не Date.now()
  try {
    await next();
  } finally {                                 // finally — інакше виняток глибше лишиться без логу
    const ms = (performance.now() - t0).toFixed(1);
    console.log(`${ctx.method} ${ctx.path} → ${ctx.status} за ${ms} мс`);
  }
};

const hits = new Map<string, number>();       // стан ЛАНЦЮГА: спільний для всіх запитів — навмисно

const rateLimit: Middleware = async (ctx, next) => {
  const n = (hits.get(ctx.ip) ?? 0) + 1;
  hits.set(ctx.ip, n);                        // квоту списано ВЖЕ ТУТ, до будь-яких перевірок
  if (n > 3) { ctx.status = 429; ctx.body = 'Забагато запитів'; return; }
  await next();
};

const auth: Middleware = async (ctx, next) => {
  if (ctx.token !== 'good-token') {
    ctx.status = 401; ctx.body = 'Потрібен токен';
    return;                                   // коротке замикання: next() не кличемо
  }
  ctx.user = 'olena';                         // стан ЗАПИТУ живе в ctx, не в самій ланці
  await next();
};

const app: Middleware = async (ctx) => {
  ctx.status = 200;
  ctx.body = `Привіт, ${ctx.user}`;
};

const handle = compose([logger, rateLimit, auth, app]);   // зібрали РАЗ

for (const token of ['good-token', 'bad', 'good-token', 'good-token']) {
  const ctx: Ctx = { method: 'GET', path: '/profile', ip: '10.0.0.7', token, status: 404, body: '' };
  await handle(ctx);
  console.log('   відповідь:', ctx.status, ctx.body);
}
