import { Order, OrderId, OrderSnapshot } from './domain';
import { OrderFulfillmentRegistry } from './order-fulfillment-registry';

/**
 * Автономний двійник у пам'яті (In-Memory Fake) із повною поведінковою відповідністю контракту.
 *
 * Переваги для тестування:
 * 1. Швидкість і детермінізм: жодної потреби в запуску контейнерів PostgreSQL/MySQL.
 * 2. Без крихких моків: не потрібно налаштовувати jest.spyOn() чи перевіряти виклики методів ORM.
 *    Тест перевіряє поведінку сутності та кінцевий стан.
 * 3. Ізоляція стану: зберігає незмінні знімки (snapshots), унеможливлюючи мутацію об'єктів
 *    за спільними посиланнями в оперативній пам'яті.
 */
export class InMemoryOrderFulfillmentRegistry implements OrderFulfillmentRegistry {
  private readonly storage: Map<string, OrderSnapshot> = new Map();

  /**
   * Наповнення двійника тестовими даними перед запуском тесту (Test Harness).
   */
  public seed(...orders: Order[]): void {
    for (const order of orders) {
      this.storage.set(order.getId().toString(), order.toSnapshot());
    }
  }

  public async claimOrdersReadyForFulfillment(batchSize: number): Promise<Order[]> {
    const readyOrders: Order[] = [];

    for (const snapshot of this.storage.values()) {
      if (readyOrders.length >= batchSize) {
        break;
      }
      if (snapshot.status === 'PENDING') {
        readyOrders.push(Order.reconstitute(snapshot));
      }
    }

    return readyOrders;
  }

  public async saveFulfilledOrders(orders: readonly Order[]): Promise<void> {
    for (const order of orders) {
      this.storage.set(order.getId().toString(), order.toSnapshot());
    }
  }

  public async findById(id: OrderId): Promise<Order | null> {
    const snapshot = this.storage.get(id.toString());
    if (!snapshot) {
      return null;
    }
    return Order.reconstitute(snapshot);
  }

  /**
   * Зручні методи для перевірки тверджень у модульних тестах:
   */
  public countFulfilled(): number {
    let count = 0;
    for (const snapshot of this.storage.values()) {
      if (snapshot.status === 'FULFILLED') {
        count++;
      }
    }
    return count;
  }

  public getAllSnapshots(): readonly OrderSnapshot[] {
    return Array.from(this.storage.values());
  }

  public clear(): void {
    this.storage.clear();
  }
}
