/**
 * Головна точка входу демонстраційного стенду:
 * 1. Контраст між застарілим сервісом (антипатерн «порт, що пахне сховищем»)
 *    та чистим рольовим портом у гексагональній архітектурі.
 * 2. Робота сценарію комплектації через SqlOrderFulfillmentAdapter.
 * 3. Автономне тестування бізнес-логіки через InMemoryOrderFulfillmentRegistry без СКБД і без моків.
 */

import { Order, OrderId, OrderItem } from './domain';
import {
  LegacyLeakyOrderRepository,
  LegacyOrderOrmEntity,
  LegacyOrderFulfillmentService,
} from './legacy-leaky-port';
import { OrderFulfillmentService } from './order-fulfillment-service';
import { SqlOrderFulfillmentAdapter } from './sql-order-fulfillment-adapter';
import { InMemoryOrderFulfillmentRegistry } from './in-memory-order-fulfillment-registry';

// Простий генератор тестових позицій замовлення
function createSampleItems(): OrderItem[] {
  return [
    { sku: 'BOOK-DDD', name: 'Domain-Driven Design', quantity: 1, unitPriceCents: 4500 },
    { sku: 'STICKER-ARCH', name: 'Clean Architecture Sticker', quantity: 3, unitPriceCents: 200 },
  ];
}

async function runLegacyDemo(): Promise<void> {
  console.log('================================================================');
  console.log('1. АНТИПАТЕРН: «ПОРТ, ЩО ПАХНЕ СХОВИЩЕМ» (Legacy Leaky Port)');
  console.log('================================================================');

  // Симуляція старого репозиторію з витоком деталей SQL
  const legacyStorage: LegacyOrderOrmEntity[] = [
    {
      db_id: 101,
      uuid_str: 'e5b7b120-1111-4a1b-8e2a-111111111111',
      customer_account_id: 42,
      status_code: 'PENDING',
      items_json: JSON.stringify(createSampleItems()),
      total_cents: 5100,
      created_epoch_ms: Date.now() - 10000,
      updated_epoch_ms: Date.now() - 10000,
      is_deleted: false,
      optimistic_lock_version: 1,
    },
    {
      db_id: 102,
      uuid_str: 'e5b7b120-2222-4a1b-8e2a-222222222222',
      customer_account_id: 43,
      status_code: 'PENDING',
      items_json: JSON.stringify(createSampleItems()),
      total_cents: 5100,
      created_epoch_ms: Date.now() - 5000,
      updated_epoch_ms: Date.now() - 5000,
      is_deleted: true, // Видалений запис (soft-delete в базі даних)
      optimistic_lock_version: 1,
    },
  ];

  const legacyRepository: LegacyLeakyOrderRepository = {
    async findOrdersWithLock(statusCode, limit, offset, forUpdate) {
      console.log(
        `   [LeakyRepo SQL] SELECT * FROM orders WHERE status='${statusCode}' LIMIT ${limit} OFFSET ${offset} FOR_UPDATE=${forUpdate}`
      );
      return legacyStorage
        .filter(r => r.status_code === statusCode)
        .slice(offset, offset + limit);
    },
    async updateRawEntity(dbId, patch) {
      console.log(`   [LeakyRepo SQL] UPDATE orders SET ${JSON.stringify(patch)} WHERE db_id=${dbId}`);
      const record = legacyStorage.find(r => r.db_id === dbId);
      if (record) {
        Object.assign(record, patch);
      }
    },
  };

  const legacyService = new LegacyOrderFulfillmentService(legacyRepository);
  // Застарілий сервіс мусить знати про limit=10, offset=0, блокування, поля таблиці БД:
  const processed = await legacyService.processBatch(10, 0);
  console.log(`[Legacy Demo] Оброблено замовлень: ${processed}`);
  console.log('Проблема: Доменний сервіс прив\'язаний до колонок БД, SQL-пагінації та блокувань!\n');
}

async function runCleanSqlAdapterDemo(): Promise<void> {
  console.log('================================================================');
  console.log('2. ЧИСТИЙ РОЛЬОВИЙ ПОРТ З SQL-АДАПТЕРОМ');
  console.log('================================================================');

  const sqlAdapter = new SqlOrderFulfillmentAdapter('worker-node-alpha');

  // Створюємо замовлення як повноцінні доменні сутності
  const order1 = Order.create(OrderId.of('a1b2c3d4-1111-4000-8000-000000000001'), createSampleItems());
  const order2 = Order.create(OrderId.of('a1b2c3d4-2222-4000-8000-000000000002'), createSampleItems());
  const order3 = Order.create(OrderId.of('a1b2c3d4-3333-4000-8000-000000000003'), createSampleItems());

  // Наповнюємо сховище через антикорупційний шар адаптера
  sqlAdapter.seedRow(order1);
  sqlAdapter.seedRow(order2);
  sqlAdapter.seedRow(order3);

  // Створюємо чистий сервіс: він залежить лише від OrderFulfillmentRegistry
  const fulfillmentService = new OrderFulfillmentService(sqlAdapter);

  console.log('Запуск першої партії комплектації (batchSize = 2):');
  const report1 = await fulfillmentService.fulfillNextBatch(2);
  console.log('Звіт партії 1:', report1);

  console.log('\nЗапуск другої партії комплектації (batchSize = 2):');
  const report2 = await fulfillmentService.fulfillNextBatch(2);
  console.log('Звіт партії 2:', report2);

  console.log('\nСтан рядків реляційної таблиці після обробки:');
  for (const row of sqlAdapter.inspectDatabaseRows()) {
    console.log(
      `   Рядок db_id=${row.db_id} | UUID=${row.uuid_str} | Статус=${row.status_code} | Заблоковано=${row.is_locked} | Версія=${row.row_version}`
    );
  }
  console.log('Успіх: SQL-адаптер повністю приховав SQL, блокування та структуру рядків від сервісу!\n');
}

async function runInMemoryTestingDemo(): Promise<void> {
  console.log('================================================================');
  console.log('3. АВТОНОМНЕ МОДУЛЬНЕ ТЕСТУВАННЯ ЧЕРЕЗ IN-MEMORY ДВІЙНИК');
  console.log('================================================================');

  // Створюємо швидкий двійник у пам'яті
  const fakeRegistry = new InMemoryOrderFulfillmentRegistry();

  const testOrderA = Order.create(OrderId.generate(), createSampleItems());
  const testOrderB = Order.create(OrderId.generate(), createSampleItems());

  // Test Harness: наповнення даними без запуску бази даних
  fakeRegistry.seed(testOrderA, testOrderB);

  // Тестуємо чистий сценарій
  const service = new OrderFulfillmentService(fakeRegistry);
  const report = await service.fulfillNextBatch(10);

  // Детерміновані перевірки (assertions)
  console.log(`[Тест] Запитано розмір партії: ${report.requestedBatchSize}`);
  console.log(`[Тест] Оброблено замовлень: ${report.fulfilledCount}`);
  console.log(`[Тест] Кількість виконаних замовлень у двійнику: ${fakeRegistry.countFulfilled()}`);

  const assertSuccess =
    report.fulfilledCount === 2 &&
    fakeRegistry.countFulfilled() === 2 &&
    report.failedCount === 0;

  if (!assertSuccess) {
    throw new Error('Тест не пройшов перевірку інваріантів!');
  }

  // Перевірка повторного виклику: не повинно бути доступних замовлень
  const secondReport = await service.fulfillNextBatch(10);
  console.log(`[Тест] Повторний виклик (готових замовлень): ${secondReport.claimedCount}`);

  if (secondReport.claimedCount !== 0) {
    throw new Error('Помилка: знайдено замовлення, які вже мали бути скомплектовані!');
  }

  console.log('\nРезультат: Усі тести виконано миттєво, без моків, без підглядання у виклики методів СКБД!');
}

async function main(): Promise<void> {
  try {
    await runLegacyDemo();
    await runCleanSqlAdapterDemo();
    await runInMemoryTestingDemo();
    console.log('\n================================================================');
    console.log('ДЕМОНСТРАЦІЮ УСПІШНО ЗАВЕРШЕНО!');
    console.log('================================================================');
  } catch (error) {
    console.error('Помилка виконання демонстрації:', error);
    process.exit(1);
  }
}

// Запуск програми
void main();
