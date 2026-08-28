// TypeScript / Node.js / OpenTelemetry Tracer & Pino Logger Integration
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import pino from 'pino';

const tracer = trace.getTracer('device-telemetry-service', '2.1.0');
const logger = pino({ name: 'device-telemetry-service' });

export async function executeCorrelatedQuery(sqlQuery: string, params: any[]) {
  // Отримуємо поточний активний спан з контексту OpenTelemetry
  const currentSpan = trace.getSpan(context.active());
  const traceId = currentSpan?.spanContext().traceId ?? 'unknown-trace-id';
  const spanId = currentSpan?.spanContext().spanId ?? 'unknown-span-id';

  const startTime = Date.now();

  // Створюємо дочірній спан клієнта бази даних
  return tracer.startActiveSpan('db:pg_exec', async (dbSpan) => {
    dbSpan.setAttribute('db.system', 'postgresql');
    dbSpan.setAttribute('db.statement', sqlQuery);

    try {
      // Симуляція запиту до бази
      const result = await dbClientQuery(sqlQuery, params);
      dbSpan.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (err: any) {
      const durationMs = Date.now() - startTime;

      // Фіксуємо помилку у спані
      dbSpan.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
      dbSpan.recordException(err);

      // Логуємо структурований JSON з обов'язковими полями trace_id та span_id
      logger.error({
        trace_id: traceId,
        span_id: spanId,
        db: { statement: sqlQuery, duration_ms: durationMs },
        err: { message: err.message, code: err.code }
      }, 'Помилка виконання SQL запиту в базі даних');

      throw err;
    } finally {
      dbSpan.end();
    }
  });
}

async function dbClientQuery(query: string, params: any[]) {
  // Імітація роботи БД
  return [];
}
