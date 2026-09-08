import http from 'node:http';
import { ResilientClient } from './resilient-client.ts';
import type { ClientConfig } from './types.ts';

// ---------------- 1. Запуск тестового HTTP-сервера ----------------
let failureMode = false;
let slowMode = false;

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok' }));
    return;
  }

  if (slowMode) {
    // Імітація завислого сокета: відповідь із затримкою 800 мс
    setTimeout(() => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ data: 'slow-payload' }));
    }, 800);
    return;
  }

  if (failureMode) {
    // Імітація каскадної аварії сторонньої служби
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Internal Gateway Outage' }));
    return;
  }

  // Нормальна швидка відповідь (20 мс)
  setTimeout(() => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ balance: 1450.50, currency: 'UAH' }));
  }, 20);
});

// ---------------- 2. Налаштування стійкого клієнта ----------------
const config: ClientConfig = {
  timeouts: {
    connectionTimeoutMs: 150,
    readTimeoutMs: 250,      // Швидке відсікання зависань сокета
    totalTimeoutMs: 800,     // Граничний бюджет на всі спроби
  },
  bulkhead: {
    maxConcurrent: 3,        // Максимум 3 паралельні запити
    maxQueueSize: 2,
  },
  circuitBreaker: {
    failureRateThreshold: 0.5,       // Розмикання при 50% збоїв
    slowCallRateThreshold: 0.5,
    slowCallDurationMs: 200,
    windowDurationMs: 2000,
    bucketCount: 5,
    minCalls: 4,                     // Мінімум 4 виклики для аналізу
    waitDurationInOpenStateMs: 1000, // 1 с на охолодження
    permittedNumberOfCallsInHalfOpenState: 2,
  },
  retry: {
    maxAttempts: 2,          // До 2 спроб
    baseDelayMs: 40,
    maxDelayMs: 150,
  },
};

const client = new ResilientClient(config);

// Кеш для демонстрації Fallback
let cachedBalance = 1000.0;

async function fetchBalance(attemptId: number): Promise<string> {
  return await client.execute(
    'get-balance',
    async (signal) => {
      const resp = await fetch('http://127.0.0.1:3999/data', { signal });
      if (!resp.ok) {
        throw new Error(`HTTP Error ${resp.status}`);
      }
      const data = await resp.json() as { balance: number };
      cachedBalance = data.balance;
      return `[${attemptId}] Успішно: Баланс = ${data.balance} UAH (стан: ${client.circuitBreaker.getState()})`;
    },
    async (err) => {
      // Fallback: повернення резервного значення з кешу
      return `[${attemptId}] ДЕГРАДАЦІЯ (Fallback): Віддано кеш ${cachedBalance} UAH | Причина: ${(err as Error).message} (стан: ${client.circuitBreaker.getState()})`;
    }
  );
}

// ---------------- 3. Демонстраційний сценарій тестування ----------------
async function runDemo() {
  await new Promise<void>((resolve) => server.listen(3999, '127.0.0.1', () => resolve()));
  console.log('=== ТЕСТОВИЙ СТЕНД: Стійкий HTTP-шлюз (TypeScript) ===\n');

  try {
    // Етап 1: Нормальна робота
    console.log('--- Етап 1: Нормальний потік викликів (стан CLOSED) ---');
    for (let i = 1; i <= 4; i++) {
      const res = await fetchBalance(i);
      console.log(res);
    }

    // Етап 2: Збій зовнішнього сервісу та розмикання запобіжника
    console.log('\n--- Етап 2: Штучний збій провайдера (HTTP 500) та розмикання ланцюга ---');
    failureMode = true;
    for (let i = 5; i <= 10; i++) {
      const res = await fetchBalance(i);
      console.log(res);
      await new Promise((r) => setTimeout(r, 60));
    }

    // Етап 3: Охолодження та зондування в HALF_OPEN
    console.log('\n--- Етап 3: Охолодження (1 с) та самозцілення провайдера ---');
    failureMode = false;
    await new Promise((r) => setTimeout(r, 1100)); // Чекаємо waitDurationInOpenStateMs

    console.log(`Стан перед зондуванням: ${client.circuitBreaker.getState()}`);
    for (let i = 11; i <= 14; i++) {
      const res = await fetchBalance(i);
      console.log(res);
      await new Promise((r) => setTimeout(r, 80));
    }

    console.log(`\nПідсумковий стан запобіжника: ${client.circuitBreaker.getState()}`);
    console.log('Демонстрацію успішно завершено: усі збої оброблені без аварійного падіння.');
  } finally {
    server.close();
  }
}

runDemo().catch(console.error);
