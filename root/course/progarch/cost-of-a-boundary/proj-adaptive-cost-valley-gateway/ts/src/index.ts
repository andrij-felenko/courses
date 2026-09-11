import { BoundarySimulator } from './boundary-simulator.ts';
import { AdaptiveBatchTimer } from './adaptive-batcher.ts';
import { DataLoaderGateway } from './data-loader-gateway.ts';
import { MetricsCollector } from './metrics.ts';
import { TerminalDashboard } from './dashboard.ts';
import type { ItemRecord } from './types.ts';

/**
 * Демонстраційний сценарій роботи асинхронного клієнтського шлюзу
 * на базі патерну DataLoader з адаптивним таймером та масками полів.
 */
async function main(): Promise<void> {
  console.log('🚀 Запуск симулятора адаптивного шлюзу подолання межі...');

  // 1. Конфігурація дорогої межі: базова затримка 15 мс (cross-service call), штраф за байти
  const boundaryConfig = {
    baseLatencyMs: 15,
    perByteLatencyMs: 0.006
  };
  const boundary = new BoundarySimulator(boundaryConfig);

  // 2. Конфігурація адаптивного таймера вікна (1 .. 25 мс, цільовий розмір 12 елементів)
  const timerConfig = {
    minWindowMs: 2,
    maxWindowMs: 25,
    targetBatchSize: 12,
    smoothingFactor: 0.25,
    maxBatchSize: 40
  };
  const timer = new AdaptiveBatchTimer(timerConfig);

  // 3. Збирач метрик та шлюз
  const metrics = new MetricsCollector(boundaryConfig.baseLatencyMs);
  const gateway = new DataLoaderGateway(boundary, timer, metrics, timerConfig.maxBatchSize);
  const dashboard = new TerminalDashboard(metrics);

  // --------------------------------------------------------------------------
  // СЦЕНАРІЙ 1: Класичний N+1 сплеск при паралельному рендерингу
  // Симулюємо ситуацію, коли 35 незалежних компонентів UI одночасно просять дані
  // користувачів, причому з різними наборами полів (Sparse Fieldsets).
  // --------------------------------------------------------------------------
  console.log('\n▶ Сценарій 1: Конкурентний сплеск 35 паралельних викликів із різними масками полів...');

  const scenario1Promises: Promise<ItemRecord>[] = [];

  for (let i = 1; i <= 35; i++) {
    const targetId = (i % 15) + 1; // повторювані ID для перевірки дедуплікації
    let requestedFields: string[];

    if (i % 3 === 0) {
      requestedFields = ['name', 'role'];
    } else if (i % 3 === 1) {
      requestedFields = ['name', 'email', 'department'];
    } else {
      requestedFields = ['name', 'status', 'permissions'];
    }

    scenario1Promises.push(gateway.load(targetId, requestedFields));
  }

  const results1 = await Promise.all(scenario1Promises);
  console.log(`  ✓ Усі 35 запитів успішно виконано. Отримано об'єктів: ${results1.length}`);
  console.log(`  Приклад першого результату (тільки запитані поля):`, results1[0]);

  dashboard.renderSummary('Сплеск паралельних N+1 запитів');

  // --------------------------------------------------------------------------
  // СЦЕНАРІЙ 2: Нерівномірний трафік (поодинокі виклики з паузами + міні-сплески)
  // Демонструє, як адаптивний таймер не заморожує одиночні виклики надовго,
  // а при появі пачки запитів автоматично групує їх.
  // --------------------------------------------------------------------------
  console.log('▶ Сценарій 2: Нерівномірний потік із чергуванням пауз та міні-батчів...');
  metrics.reset();
  timer.reset();

  // Одиночний виклик
  await gateway.load(101, ['name', 'status']);
  await new Promise((r) => setTimeout(r, 40)); // пауза між активностями

  // Міні-сплеск із 6 викликів
  const burst1 = [
    gateway.load(102, ['name', 'department']),
    gateway.load(103, ['name', 'role']),
    gateway.load(104, ['name', 'email']),
    gateway.load(105, ['name', 'status']),
    gateway.load(106, ['name', 'permissions']),
    gateway.load(107, ['name', 'preferences'])
  ];
  await Promise.all(burst1);
  await new Promise((r) => setTimeout(r, 50));

  // Ще один одиночний виклик
  await gateway.load(108, ['name', 'email']);

  dashboard.renderSummary('Нерівномірний потік із самоналаштуванням вікна');

  console.log('✅ Усі симуляційні сценарії успішно завершено.');
}

void main();
