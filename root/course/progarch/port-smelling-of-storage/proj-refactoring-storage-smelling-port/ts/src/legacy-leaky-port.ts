/**
 * Демонстрація антипатерну «порту, що пахне сховищем» (Port smelling of storage).
 *
 * Тут інтерфейс порту був створений «ззовні всередину» (від моделі бази даних)
 * замість проєктування від потреб доменного сценарію:
 * 1. Витік типів ORM: сервіс працює з сирими рядками таблиць бази даних.
 * 2. Витік параметрів SQL: сервіс змушений знати про limit/offset і самостійно рахувати сторінки.
 * 3. Витік деталей транзакцій: прапорець forUpdate (SELECT FOR UPDATE) просочився в інтерфейс.
 * 4. Технічні поля БД: сервіс знає про soft-delete (is_deleted), версіонування та внутрішній числовий ID.
 */

export interface LegacyOrderOrmEntity {
  db_id: number; // Первинний числовий auto-increment ключ СКБД
  uuid_str: string;
  customer_account_id: number;
  status_code: string; // 'PENDING', 'FULFILLED' тощо
  items_json: string;
  total_cents: number;
  created_epoch_ms: number;
  updated_epoch_ms: number;
  is_deleted: boolean; // Технічний прапорець soft-delete
  optimistic_lock_version: number;
}

/**
 * Антипатерн: інтерфейс репозиторію, який повністю повторює технічні можливості SQL.
 */
export interface LegacyLeakyOrderRepository {
  /**
   * Метод змушує бізнес-код вирішувати інфраструктурні проблеми:
   * пагінацію через зміщення (offset) та вибір режиму блокування рядків (forUpdate).
   */
  findOrdersWithLock(
    statusCode: string,
    limit: number,
    offset: number,
    forUpdate: boolean
  ): Promise<LegacyOrderOrmEntity[]>;

  /**
   * Оновлення за технічним первинним ключем таблиці.
   */
  updateRawEntity(
    dbId: number,
    patch: Partial<LegacyOrderOrmEntity>
  ): Promise<void>;
}

/**
 * Застарілий сервіс комплектації:
 * Бізнес-логіка розмита через керування зміщенням сторінок і безпосереднє
 * мутування колонок таблиць бази даних.
 */
export class LegacyOrderFulfillmentService {
  constructor(private readonly repository: LegacyLeakyOrderRepository) {}

  /**
   * Сервіс змушений передавати параметри пагінації бази та піклуватися
   * про блокування рядків у транзакції, що грубо порушує принцип інверсії залежностей.
   */
  public async processBatch(batchSize: number, pageOffset: number): Promise<number> {
    console.log(
      `[LegacyOrderFulfillmentService] Запит до БД: status='PENDING', limit=${batchSize}, offset=${pageOffset}, forUpdate=true`
    );

    // Доменний сервіс напряму керує SQL-блокуванням рядків і пагінацією!
    const records = await this.repository.findOrdersWithLock(
      'PENDING',
      batchSize,
      pageOffset,
      true // Прапорець forUpdate витік із реляційного сховища в сервіс!
    );

    let updatedCount = 0;

    for (const record of records) {
      // Сервіс змушений перевіряти технічні деталі збереження
      if (record.is_deleted) {
        console.log(`[LegacyOrderFulfillmentService] Пропуск видаленого запису db_id=${record.db_id}`);
        continue;
      }

      // Немає доменної моделі: пряме оновлення полів таблиці
      console.log(
        `[LegacyOrderFulfillmentService] Мутація запису БД db_id=${record.db_id} (${record.uuid_str})`
      );

      await this.repository.updateRawEntity(record.db_id, {
        status_code: 'FULFILLED',
        updated_epoch_ms: Date.now(),
        optimistic_lock_version: record.optimistic_lock_version + 1,
      });

      updatedCount++;
    }

    return updatedCount;
  }
}
