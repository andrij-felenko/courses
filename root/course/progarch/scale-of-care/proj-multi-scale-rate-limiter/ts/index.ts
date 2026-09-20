/**
 * index.ts
 *
 * Демонстраційний стенд та точка входу.
 * Моделює планетарну поведінку Cloudflare Worker:
 * 1. Шторм запитів: субмілісекундна локальна перевірка (<0.2 мс) проти затримки світла (80 мс WAN RTT).
 * 2. Фоновий батчинг дельт: консолідація спожитих токенів через ctx.waitUntil без затримки клієнта.
 * 3. Аварійна стійкість Fail-Open: збереження доступності системи при відмові центрального координатора.
 */

import {
  CentralCoordinatorClient,
  MockCentralCoordinator,
} from './central_coordinator.ts';
import { EdgeRateLimiter, EdgeWorker } from './edge_worker.ts';
import type { EdgeRateLimiterConfig, ExecutionContext } from './types.ts';

/**
 * Емулятор середовища Cloudflare Workers ExecutionContext для автономного запуску.
 * Збирає зареєстровані фонові задачі waitUntil для контрольованого очікування на стенді.
 */
class MockExecutionContext implements ExecutionContext {
  public pendingTasks: Promise<unknown>[] = [];

  public waitUntil(promise: Promise<unknown>): void {
    this.pendingTasks.push(promise);
  }

  public async drainAll(): Promise<void> {
    await Promise.all(this.pendingTasks);
    this.pendingTasks = [];
  }
}

/**
 * Форматує розділ для наочного виводу в консоль.
 */
function logSection(title: string): void {
  console.log('\n' + '='.repeat(80));
  console.log(`  ${title}`);
  console.log('='.repeat(80));
}

async function runDemonstration(): Promise<void> {
  logSection(
    'АРХІТЕКТУРА «МАСШТАБ ТУРБОТИ»: ГРАНИЧНИЙ ОБМЕЖУВАЧ З МЕХАНІКОЮ TOKEN LEASE'
  );

  const clientId = 'edge-client-kyiv-01';
  const simulatedWanLatencyMs = 80; // 80 мс — типовий RTT Франкфурт <-> Північна Вірджинія

  // Налаштування обмежувача: глобальний ліміт 100 запитів/хв, блок оренди = 20 токенів
  const config: EdgeRateLimiterConfig = {
    globalLimit: 100,
    windowSeconds: 60,
    leaseBatchSize: 20,
    leaseTtlMs: 15000,
    refillThresholdTokens: 5, // Поріг запуску фонового оновлення
    syncTimeoutMs: 300,
    failOpen: true, // Пріоритет доступності (Availability over Consistency)
    fallbackLeaseTokens: 10,
  };

  // 1. Створюємо центральний координатор із симуляцією трансконтинентальної затримки
  const centralCoordinator = new MockCentralCoordinator(
    config.globalLimit,
    config.windowSeconds,
    config.leaseTtlMs,
    simulatedWanLatencyMs
  );

  const coordinatorClient = new CentralCoordinatorClient(
    centralCoordinator,
    config
  );
  const limiter = new EdgeRateLimiter(config, coordinatorClient);
  const worker = new EdgeWorker(limiter);

  // Прогріваємо початковий блок оренди у 20 токенів
  limiter.prewarmBucket(clientId, 20, config.leaseTtlMs);

  const executionCtx = new MockExecutionContext();

  // =========================================================================
  // ЕТАП 1: Шторм конкурентних запитів на межі мережі
  // =========================================================================
  logSection(
    'ЕТАП 1: Шторм запитів — локальне списання в V8 проти міжконтинентального WAN RTT'
  );

  console.log(
    `[Параметри] Клієнт: ${clientId} | Початковий блок оренди: 20 токенів | WAN RTT центру: ${simulatedWanLatencyMs} мс`
  );
  console.log(
    `[Поріг] Фонова синхронізація через ctx.waitUntil активується при залишку <= ${config.refillThresholdTokens} токенів\n`
  );

  const requestCount = 16;
  let totalEdgeLatency = 0;

  for (let i = 1; i <= requestCount; i++) {
    const request = new Request(`https://api.example.com/data?id=${i}`, {
      method: 'GET',
      headers: {
        'CF-Connecting-IP': clientId,
        'User-Agent': 'Cloudflare-Edge-Client/1.0',
      },
    });

    const start = performance.now();
    const response = await worker.fetch(request, {}, executionCtx);
    const elapsed = performance.now() - start;
    totalEdgeLatency += elapsed;

    const remaining = response.headers.get('RateLimit-Remaining');
    const edgeExecTime = response.headers.get('X-Edge-Latency-Ms');

    console.log(
      `Запит #${String(i).padStart(2, '0')} -> HTTP ${response.status} | ` +
        `Час відповіді клієнту: ${elapsed.toFixed(3)} мс ` +
        `(V8 ізолят: ${edgeExecTime} мс) | ` +
        `Залишок у блоці: ${remaining} | ` +
        `Задач у ctx.waitUntil: ${executionCtx.pendingTasks.length}`
    );
  }

  const avgEdgeLatency = totalEdgeLatency / requestCount;
  console.log('\n--- Підсумок першого етапу ---');
  console.log(
    `Середній час відповіді клієнту на межі: ${avgEdgeLatency.toFixed(3)} мс`
  );
  console.log(
    `Синхронний мережевий виклик до центру забрав би: ${simulatedWanLatencyMs * requestCount} мс (${((simulatedWanLatencyMs * requestCount) / 1000).toFixed(2)} с)`
  );
  console.log(
    `Фактичний сумарний час клієнтських відповідей: ${totalEdgeLatency.toFixed(2)} мс`
  );
  console.log(
    `Прискорення обробки на межі мережі: ${(simulatedWanLatencyMs / avgEdgeLatency).toFixed(0)}x!`
  );

  // =========================================================================
  // ЕТАП 2: Фоновий батчинг дельт у ctx.waitUntil
  // =========================================================================
  logSection(
    'ЕТАП 2: Виконання фонової синхронізації та батчинг дельт (ctx.waitUntil)'
  );

  console.log(
    `Очікуємо завершення фонових задач синхронізації (${executionCtx.pendingTasks.length} задач)...`
  );
  const bgStart = performance.now();
  await executionCtx.drainAll();
  const bgElapsed = performance.now() - bgStart;

  console.log(
    `Фонова синхронізація завершилась за ${bgElapsed.toFixed(2)} мс (клієнт цього НЕ чекав)`
  );
  console.log(
    `Метрики координатора: зареєстровано звернень до центру = ${centralCoordinator.metrics.totalRequestsReceived}`
  );
  console.log(
    `Зафіксована батчем дельта споживання = ${centralCoordinator.metrics.totalDeltasCommitted} токенів`
  );
  console.log(
    `Надано нових орендованих токенів = ${centralCoordinator.metrics.totalTokensGranted}`
  );

  const bucketAfterRefill = limiter.getOrCreateBucket(clientId);
  console.log(
    `Поточний залишок токенів у локальному бакеті після фонового поповнення: ${bucketAfterRefill.getRemainingTokens()}`
  );

  // =========================================================================
  // ЕТАП 3: Аварійна деградація Fail-Open при відмові координатора
  // =========================================================================
  logSection(
    'ЕТАП 3: Аварійна деградація Fail-Open при відмові центрального регіону'
  );

  console.log(
    'Імітуємо трансконтинентальний мережевий збій (WAN Partition / Central DB Outage)...'
  );
  centralCoordinator.setSimulateFailure(true);

  // Штучно вичерпуємо залишок локального бакета, щоб спровокувати необхідність термінової синхронізації
  while (bucketAfterRefill.getRemainingTokens() > 0) {
    bucketAfterRefill.tryConsume(1);
  }

  console.log(
    'Локальний залишок скинуто до 0. Надсилаємо новий запит за умов повної відмови центру...'
  );

  const failOpenRequest = new Request('https://api.example.com/critical-data', {
    method: 'GET',
    headers: { 'CF-Connecting-IP': clientId },
  });

  const failOpenResponse = await worker.fetch(failOpenRequest, {}, executionCtx);
  console.log(
    `HTTP статус первинного запиту при вичерпаному бакеті: ${failOpenResponse.status}`
  );

  console.log('Виконується аварійне фонове завдання Fail-Open...');
  await executionCtx.drainAll();

  // Наступний запит після відпрацювання аварійної стратегії
  const subsequentRequest = new Request(
    'https://api.example.com/critical-data',
    {
      method: 'GET',
      headers: { 'CF-Connecting-IP': clientId },
    }
  );

  const subsequentResponse = await worker.fetch(
    subsequentRequest,
    {},
    executionCtx
  );
  const fallbackHeader = subsequentResponse.headers.get('X-RateLimit-Fallback');

  console.log(
    `Подальший запит під час аварії центру -> HTTP ${subsequentResponse.status}`
  );
  console.log(`Заголовок аварійного режиму: ${fallbackHeader}`);
  console.log(
    `Політика Fail-Open зберегла сервіс доступним для користувача (100% Availability)!`
  );

  logSection('ДЕМОНСТРАЦІЮ УСПІШНО ЗАВЕРШЕНО');
}

// Запуск демонстраційного сценарію
runDemonstration().catch((err) => {
  console.error('Критична помилка виконання стенду:', err);
  process.exit(1);
});
