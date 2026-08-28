// TypeScript / Node.js / Express / Pino / AsyncLocalStorage
import express, { Request, Response, NextFunction } from 'express';
import { AsyncLocalStorage } from 'async_hooks';
import pino from 'pino';
import { randomBytes } from 'crypto';

interface TraceStore {
  traceId: string;
  spanId: string;
  sampled: boolean;
}

const traceStorage = new AsyncLocalStorage<TraceStore>();

// Парсинг або генерація W3C traceparent
function getOrGenerateTraceContext(req: Request): TraceStore {
  const header = req.headers['traceparent'] as string;
  if (header && header.startsWith('00-')) {
    const parts = header.split('-');
    if (parts.length >= 4) {
      return {
        traceId: parts[1],
        spanId: parts[2],
        sampled: parts[3] === '01'
      };
    }
  }
  return {
    traceId: randomBytes(16).toString('hex'),
    spanId: randomBytes(8).toString('hex'),
    sampled: true
  };
}

// Pino логер, що динамічно витягує trace_id з AsyncLocalStorage
const logger = pino({
  mixin() {
    const store = traceStorage.getStore();
    return {
      trace_id: store?.traceId ?? 'none',
      span_id: store?.spanId ?? 'none'
    };
  },
  base: { service: 'device-telemetry-service' }
});

const app = express();

// Middleware прокидання контексту
app.use((req: Request, res: Response, next: NextFunction) => {
  const context = getOrGenerateTraceContext(req);

  // Прокидаємо traceparent у вихідні заголовки відповіді
  res.setHeader('traceparent', `00-${context.traceId}-${context.spanId}-${context.sampled ? '01' : '00'}`);

  // Запускаємо ланцюг обробників всередині AsyncLocalStorage
  traceStorage.run(context, () => {
    logger.info({ path: req.path }, 'HTTP запит прийнято в обробку');
    next();
  });
});

app.get('/api/v2/telemetry/history', async (req: Request, res: Response) => {
  try {
    logger.info('Виконання запиту агрегації телеметрії');
    // Симуляція запиту до БД
    res.json({ status: 'ok', data: [] });
  } catch (err: any) {
    logger.error({ err }, 'Помилка виконання запиту агрегації');
    res.status(500).json({ code: 'internal_error' });
  }
});
