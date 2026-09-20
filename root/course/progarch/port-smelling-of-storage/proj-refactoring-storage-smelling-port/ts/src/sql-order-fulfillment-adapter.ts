import { Order, OrderId, OrderSnapshot, OrderStatus } from './domain';
import { OrderFulfillmentRegistry } from './order-fulfillment-registry';

/**
 * Внутрішня реляційна схема рядка таблиці 'orders' у реляційній базі даних.
 * Вона ніколи не виходить за межі цього адаптера!
 */
export interface SqlDatabaseOrderRow {
  db_id: number;
  uuid_str: string;
  status_code: string;
  items_json: string;
  total_amount_cents: number;
  created_at_iso: string;
  fulfilled_at_iso: string | null;
  is_locked: boolean;
  locked_by_worker: string | null;
  locked_at_iso: string | null;
  row_version: number;
}

/**
 * Вторинний адаптер реляційного сховища:
 * 1. Працює як антикорупційний шар (ACL) між SQL-таблицею та доменом.
 * 2. Повністю інкапсулює пакетовану пагінацію (домен про неї не знає).
 * 3. Інкапсулює блокування записів (SELECT ... FOR UPDATE) для запобігання стану гонитви.
 * 4. Виконує двосторонній мапінг між SQL-рядками та доменними сутностями.
 */
export class SqlOrderFulfillmentAdapter implements OrderFulfillmentRegistry {
  // Симуляція таблиці реляційної бази даних з транзакційним станом
  private readonly databaseRows: Map<number, SqlDatabaseOrderRow> = new Map();
  private autoIncrementSequence = 1;

  constructor(private readonly workerIdentifier: string = 'worker-1') {}

  /**
   * Наповнення симульованої бази даних початковими записами (для стенду та тестів).
   */
  public seedRow(order: Order): void {
    const snapshot = order.toSnapshot();
    const dbId = this.autoIncrementSequence++;

    const row: SqlDatabaseOrderRow = {
      db_id: dbId,
      uuid_str: snapshot.id,
      status_code: snapshot.status,
      items_json: JSON.stringify(snapshot.items),
      total_amount_cents: snapshot.totalAmountCents,
      created_at_iso: snapshot.createdAt.toISOString(),
      fulfilled_at_iso: snapshot.fulfilledAt ? snapshot.fulfilledAt.toISOString() : null,
      is_locked: false,
      locked_by_worker: null,
      locked_at_iso: null,
      row_version: 1,
    };

    this.databaseRows.set(dbId, row);
  }

  /**
   * Реалізація порту:
   * Інкапсулює SQL-запит виду:
   * SELECT * FROM orders
   * WHERE status_code = 'PENDING' AND is_locked = FALSE
   * ORDER BY created_at_iso ASC
   * LIMIT :batchSize
   * FOR UPDATE SKIP LOCKED;
   */
  public async claimOrdersReadyForFulfillment(batchSize: number): Promise<Order[]> {
    console.log(
      `[SqlAdapter:${this.workerIdentifier}] Виконання SQL: SELECT FOR UPDATE з лімітом ${batchSize}...`
    );

    const claimedRows: SqlDatabaseOrderRow[] = [];

    // Пошук доступних незаблокованих записів у статусі PENDING
    for (const row of this.databaseRows.values()) {
      if (claimedRows.length >= batchSize) {
        break;
      }

      if (row.status_code === 'PENDING' && !row.is_locked) {
        // Блокування рядка (емуляція транзакційного блокування FOR UPDATE)
        row.is_locked = true;
        row.locked_by_worker = this.workerIdentifier;
        row.locked_at_iso = new Date().toISOString();
        claimedRows.push(row);
      }
    }

    console.log(
      `[SqlAdapter:${this.workerIdentifier}] Заблоковано та зарезервовано ${claimedRows.length} рядків у БД`
    );

    // Мапінг реляційних рядків у чисті доменні сутності
    return claimedRows.map(row => this.mapRowToDomain(row));
  }

  /**
   * Реалізація порту:
   * Інкапсулює SQL-запит виду:
   * UPDATE orders SET
   *   status_code = :status,
   *   fulfilled_at_iso = :fulfilledAt,
   *   is_locked = FALSE,
   *   locked_by_worker = NULL,
   *   row_version = row_version + 1
   * WHERE uuid_str = :uuid;
   */
  public async saveFulfilledOrders(orders: readonly Order[]): Promise<void> {
    console.log(
      `[SqlAdapter:${this.workerIdentifier}] Виконання SQL: пакетний UPDATE та зняття блокувань для ${orders.length} замовлень...`
    );

    for (const order of orders) {
      const snapshot = order.toSnapshot();
      const row = this.findRowByUuid(snapshot.id);

      if (!row) {
        throw new Error(`[SqlAdapter] Запис у базі для UUID ${snapshot.id} не знайдено!`);
      }

      // Оновлення полів реляційної таблиці та розблокування
      row.status_code = snapshot.status;
      row.fulfilled_at_iso = snapshot.fulfilledAt ? snapshot.fulfilledAt.toISOString() : null;
      row.is_locked = false;
      row.locked_by_worker = null;
      row.locked_at_iso = null;
      row.row_version += 1;
    }
  }

  public async findById(id: OrderId): Promise<Order | null> {
    const row = this.findRowByUuid(id.toString());
    if (!row) return null;
    return this.mapRowToDomain(row);
  }

  /**
   * Допоміжний метод інспекції для демонстраційного стенду:
   * дозволяє перевірити реальний стан таблиці бази даних.
   */
  public inspectDatabaseRows(): readonly SqlDatabaseOrderRow[] {
    return Array.from(this.databaseRows.values());
  }

  private findRowByUuid(uuid: string): SqlDatabaseOrderRow | undefined {
    for (const row of this.databaseRows.values()) {
      if (row.uuid_str === uuid) {
        return row;
      }
    }
    return undefined;
  }

  /**
   * Антикорупційний шар: перетворення реляційного рядка таблиці в доменну сутність.
   */
  private mapRowToDomain(row: SqlDatabaseOrderRow): Order {
    const snapshot: OrderSnapshot = {
      id: row.uuid_str,
      status: row.status_code as OrderStatus,
      items: JSON.parse(row.items_json),
      totalAmountCents: row.total_amount_cents,
      createdAt: new Date(row.created_at_iso),
      fulfilledAt: row.fulfilled_at_iso ? new Date(row.fulfilled_at_iso) : null,
    };

    return Order.reconstitute(snapshot);
  }
}
