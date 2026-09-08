import http from 'node:http';
import { OutboxRepository } from './outbox-repository.ts';
import { IdempotentHttpClient } from './http-client.ts';
import { OutboxWorker } from './outbox-worker.ts';

// ---------------- 1. Запуск тестового HTTP-сервера зовнішньої служби ----------------
const processedIdempotencyKeys = new Set<string>();
let temporaryFailureResolved = false;

const server = http.createServer(async (req, res) => {
  const idemKey = req.headers['idempotency-key'] as string;
  let body = '';
  for await (const chunk of req) body += chunk;
  const payload = body ? JSON.parse(body) : {};

  // Сценарій 1: Помилка 400 (невірні реквізити) -> демонстрація миттєвого DLQ
  if (payload.orderId === 'ORD-400') {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Недійсні реквізити платежу (Некоректний IBAN)' }));
    return;
  }

  // Сценарій 2: Постійний збій 500 -> вичерпання ретраїв і перехід у DLQ
  if (payload.orderId === 'ORD-500') {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Фатальна відмова платіжного шлюзу' }));
    return;
  }

  // Сценарій 3: Тимчасовий збій 503 з одужанням на повторній спробі
  if (payload.orderId === 'ORD-503' && !temporaryFailureResolved) {
    temporaryFailureResolved = true; // Наступного разу відповість успіхом
    res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Сервіс тимчасово перевантажений, спробуйте пізніше' }));
    return;
  }

  // Сценарій 4: Штатний успішний виклик (200 OK)
  if (processedIdempotencyKeys.has(idemKey)) {
    // Демонстрація ідемпотентності: повторний виклик повертає успіх без повторної проводки
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ALREADY_PROCESSED', orderId: payload.orderId }));
    return;
  }

  processedIdempotencyKeys.add(idemKey);
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'SUCCESS', transactionId: `tx-${Date.now()}` }));
});

// ---------------- 2. Демонстраційний запуск конвеєра Outbox ----------------
async function runDemo() {
  await new Promise<void>((resolve) => server.listen(4002, '127.0.0.1', resolve));
  const targetUrl = 'http://127.0.0.1:4002/webhook/payments';

  console.log('=== ТЕСТОВИЙ СТЕНД: Transactional Outbox Worker (TypeScript) ===\n');

  const repository = new OutboxRepository();
  const httpClient = new IdempotentHttpClient(2000);

  // Створення бізнес-замовлень в одній SQL-транзакції з аутбоксом
  console.log('--- Крок 1: Атомарний запис подій у таблицю Outbox ---');

  await repository.saveWithinTransaction({
    aggregateType: 'Order',
    aggregateId: 'ORD-101',
    eventType: 'PaymentRequested',
    payload: { orderId: 'ORD-101', amount: 450.0, currency: 'UAH' },
    idempotencyKey: 'idem-ord-101-v1',
  });

  await repository.saveWithinTransaction({
    aggregateType: 'Order',
    aggregateId: 'ORD-503',
    eventType: 'PaymentRequested',
    payload: { orderId: 'ORD-503', amount: 820.0, currency: 'UAH' },
    idempotencyKey: 'idem-ord-503-v1',
    maxAttempts: 3,
  });

  await repository.saveWithinTransaction({
    aggregateType: 'Order',
    aggregateId: 'ORD-400',
    eventType: 'PaymentRequested',
    payload: { orderId: 'ORD-400', amount: 99.0, currency: 'UAH' },
    idempotencyKey: 'idem-ord-400-v1',
  });

  await repository.saveWithinTransaction({
    aggregateType: 'Order',
    aggregateId: 'ORD-500',
    eventType: 'PaymentRequested',
    payload: { orderId: 'ORD-500', amount: 1500.0, currency: 'UAH' },
    idempotencyKey: 'idem-ord-500-v1',
    maxAttempts: 2, // Лише 2 спроби для швидкої демонстрації DLQ
  });

  console.log(`Створено 4 задачі в аутбоксі: ORD-101 (норма), ORD-503 (тимчасовий збій), ORD-400 (4xx), ORD-500 (вихід у DLQ)\n`);

  // Запуск двох паралельних воркерів (конкурентна вибірка SKIP LOCKED)
  console.log('--- Крок 2: Запуск пулу воркерів (Worker-A та Worker-B із SKIP LOCKED) ---');

  const workerA = new OutboxWorker(
    {
      workerId: 'Worker-A',
      batchSize: 2,
      pollIntervalMs: 50,
      baseDelayMs: 40,
      maxDelayMs: 200,
      defaultMaxAttempts: 3,
    },
    repository,
    httpClient,
    targetUrl
  );

  const workerB = new OutboxWorker(
    {
      workerId: 'Worker-B',
      batchSize: 2,
      pollIntervalMs: 50,
      baseDelayMs: 40,
      maxDelayMs: 200,
      defaultMaxAttempts: 3,
    },
    repository,
    httpClient,
    targetUrl
  );

  workerA.start();
  workerB.start();

  // Очікуємо обробки та завершення ретраїв
  await new Promise((r) => setTimeout(r, 1200));

  await workerA.stop();
  await workerB.stop();
  server.close();

  console.log('\n--- Крок 3: Підсумковий стан сховища Outbox ---');
  const metrics = repository.getMetrics();
  console.log(`Всього задач: ${metrics.total}`);
  console.log(`Успішно завершено (COMPLETED): ${metrics.completed}`);
  console.log(`Ізольовано в DLQ (DEAD_LETTER): ${metrics.deadLetter}`);
  console.log(`В очікуванні (PENDING): ${metrics.pending}`);

  console.log('\nДеталізація записів:');
  for (const m of repository.getAll()) {
    console.log(` - [${m.status}] ${m.aggregateId}: спроб ${m.attempts}/${m.maxAttempts} | помилка: ${m.lastError || 'немає'}`);
  }

  console.log('\nДемонстрацію успішно завершено: усі задачі оброблено згідно з контрактами надійності.');
}

runDemo().catch(console.error);
