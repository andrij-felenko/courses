import { MockCentralBackend } from './central-backend.ts';
import { EdgeRateLimiter } from './edge-limiter.ts';
import type { ExecutionContext, RateLimitConfig } from './types.ts';

// Конфігурація периферійного обмежувача
const config: RateLimitConfig = {
  limit: 20,              // 20 запитів на хвилину для клієнта
  windowMs: 60_000,       // Вікно: 1 хвилина
  leaseSize: 5,           // Пачка оренди: 5 токенів на воркер
  flushIntervalMs: 500,   // Фонове скидання кожні 500 мс
  maxBatchSize: 10,       // Максимальний буфер батчу: 10 записів
};

const centralBackend = new MockCentralBackend();
const edgeLimiter = new EdgeRateLimiter(centralBackend, config);

/**
 * WorkerHandler: обробка вхідного HTTP-запиту в середовищі Cloudflare Workers.
 */
export const WorkerHandler = {
  async fetch(request: Request, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const clientIp = request.headers.get('cf-connecting-ip') || '192.168.1.50';
    const rateLimitKey = `client:${clientIp}`;

    const decision = await edgeLimiter.check(rateLimitKey, ctx);

    // Стандартні заголовки IETF RateLimit
    const headers = new Headers({
      'Content-Type': 'application/json',
      'X-RateLimit-Limit': decision.limit.toString(),
      'X-RateLimit-Remaining': decision.remaining.toString(),
      'X-RateLimit-Reset': Math.ceil(decision.resetInMs / 1000).toString(),
      'X-RateLimit-Source': decision.source,
    });

    if (!decision.allowed) {
      return new Response(
        JSON.stringify({
          error: 'Too Many Requests',
          message: decision.reason,
          retryAfterSeconds: Math.ceil(decision.resetInMs / 1000),
        }),
        { status: 429, headers }
      );
    }

    return new Response(
      JSON.stringify({
        status: 'OK',
        message: 'Запит успішно оброблено на периферійному вузлі',
        decision: decision.reason,
      }),
      { status: 200, headers }
    );
  },
};

/**
 * Демонстраційний запуск для перевірки всіх режимів роботи.
 */
async function runDemo(): Promise<void> {
  console.log('=== 1. Початкове поповнення оренди та швидкі периферійні запити ===');

  const backgroundTasks: Promise<unknown>[] = [];
  const mockCtx: ExecutionContext = {
    waitUntil: (p: Promise<unknown>) => {
      backgroundTasks.push(p);
    },
  };

  // Запит #1: початкове звернення до центрального сховища за орендою
  const t1 = performance.now();
  const res1 = await WorkerHandler.fetch(
    new Request('https://api.digitalhome.internal/sensor/temp'),
    mockCtx
  );
  console.log(`Запит 1: HTTP ${res1.status} | Тривалість: ${(performance.now() - t1).toFixed(2)} мс | Залишок: ${res1.headers.get('X-RateLimit-Remaining')}`);

  // Запити #2..#5: миттєве виконання з локальної пам'яті ізоляту V8 (0.05–0.2 мс!)
  for (let i = 2; i <= 5; i++) {
    const tStart = performance.now();
    const res = await WorkerHandler.fetch(
      new Request('https://api.digitalhome.internal/sensor/temp'),
      mockCtx
    );
    console.log(`Запит ${i}: HTTP ${res.status} | Тривалість: ${(performance.now() - tStart).toFixed(2)} мс | Залишок: ${res.headers.get('X-RateLimit-Remaining')}`);
  }

  console.log('\n=== 2. Асинхронне фонове скидання накопичених батчів через waitUntil ===');
  console.log(`Фонових задач у черзі: ${backgroundTasks.length}`);
  await Promise.all(backgroundTasks);
  console.log('Усі фонові батчі успішно збережено в центральному координаторі без затримки для клієнта.');

  console.log('\n=== 3. Поведінка при відмові центрального сховища (Fail-Open) ===');
  centralBackend.setSimulateFailure(true);

  // Новий клієнт без попередньої локальної оренди звертається під час падіння центральної бази
  const tFail = performance.now();
  const resFail = await WorkerHandler.fetch(
    new Request('https://api.digitalhome.internal/sensor/temp', {
      headers: { 'cf-connecting-ip': '203.0.113.199' },
    }),
    mockCtx
  );
  console.log(`Fallback запит: HTTP ${resFail.status} | Джерело: ${resFail.headers.get('X-RateLimit-Source')} | Час: ${(performance.now() - tFail).toFixed(2)} мс`);
}

// Запуск демонстрації
if (process.env.NODE_ENV !== 'production') {
  runDemo().catch(console.error);
}

export default WorkerHandler;
