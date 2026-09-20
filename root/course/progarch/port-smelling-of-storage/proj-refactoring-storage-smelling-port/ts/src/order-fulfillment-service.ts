import { Order, DomainError } from './domain';
import { OrderFulfillmentRegistry } from './order-fulfillment-registry';

export interface FulfillmentReport {
  readonly requestedBatchSize: number;
  readonly claimedCount: number;
  readonly fulfilledCount: number;
  readonly failedCount: number;
  readonly fulfilledOrderIds: readonly string[];
  readonly failureDetails: readonly { orderId: string; reason: string }[];
}

/**
 * Чистий доменний сценарій виконання замовлень (Use Case).
 * Він повністю захищений від деталей баз даних, SQL чи ORM:
 * взаємодіє виключно з рольовим портом OrderFulfillmentRegistry.
 */
export class OrderFulfillmentService {
  constructor(private readonly registry: OrderFulfillmentRegistry) {}

  /**
   * Виконує комплектацію наступної доступної партії замовлень.
   */
  public async fulfillNextBatch(batchSize: number = 10): Promise<FulfillmentReport> {
    if (batchSize <= 0) {
      throw new DomainError('Розмір партії для комплектації має бути більшим за нуль.');
    }

    // Отримання партії через рольовий контракт без знання про offset, limit чи блокування
    const orders = await this.registry.claimOrdersReadyForFulfillment(batchSize);

    const successfullyFulfilled: Order[] = [];
    const fulfilledIds: string[] = [];
    const failures: { orderId: string; reason: string }[] = [];

    for (const order of orders) {
      const orderIdStr = order.getId().toString();
      try {
        // Виклик бізнес-методу сутності з контролем переходів стану та інваріантів
        order.fulfill(new Date());
        successfullyFulfilled.push(order);
        fulfilledIds.push(orderIdStr);
      } catch (error) {
        const reason = error instanceof Error ? error.message : String(error);
        failures.push({ orderId: orderIdStr, reason });
      }
    }

    // Збереження результату через рольовий порт
    if (successfullyFulfilled.length > 0) {
      await this.registry.saveFulfilledOrders(successfullyFulfilled);
    }

    return {
      requestedBatchSize: batchSize,
      claimedCount: orders.length,
      fulfilledCount: successfullyFulfilled.length,
      failedCount: failures.length,
      fulfilledOrderIds: fulfilledIds,
      failureDetails: failures,
    };
  }
}
