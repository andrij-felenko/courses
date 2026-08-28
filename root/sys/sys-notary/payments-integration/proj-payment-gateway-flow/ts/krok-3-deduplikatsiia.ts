export interface OrderRecord {
  id: string;
  status: "PENDING" | "PAID" | "CANCELED" | "REFUNDED";
  amountCents: number;
}

export interface LedgerLine {
  accountId: string; // Наприклад: '1010-PSP-CLEARING', '4010-REVENUE', '5010-FEES'
  debitCents: number;
  creditCents: number;
}

export class OrderFulfillmentCoordinator {
  private readonly processedEventIds = new Set<string>();
  private readonly orders = new Map<string, OrderRecord>();
  private readonly ledger: LedgerLine[] = [];

  constructor() {
    // Ініціалізація тестового замовлення в БД
    this.orders.set("ord_884920", {
      id: "ord_884920",
      status: "PENDING",
      amountCents: 10990,
    });
  }

  /**
   * Атомарна та ідемпотентна обробка події payment_intent.succeeded.
   */
  async handlePaymentSucceeded(event: {
    id: string;
    data: { object: { id: string; amount: number; metadata: { order_id: string } } };
  }): Promise<{ status: "PROCESSED" | "ALREADY_PROCESSED" | "IGNORED_OLD_STATE" }> {
    const eventId = event.id;

    // 1. Дедуплікація: перевірка чи подія вже оброблялася
    if (this.processedEventIds.has(eventId)) {
      return { status: "ALREADY_PROCESSED" };
    }

    const orderId = event.data.object.metadata.order_id;
    const order = this.orders.get(orderId);
    if (!order) {
      throw new Error(`Замовлення ${orderId} не знайдено в локальній базі`);
    }

    // 2. Монотонний захист станів (State Guard)
    if (order.status === "PAID") {
      this.processedEventIds.add(eventId);
      return { status: "IGNORED_OLD_STATE" };
    }

    // 3. Атомарне оновлення замовлення та фіксація у фінансовому журналі (Ledger)
    order.status = "PAID";

    const amount = event.data.object.amount;
    const estimatedFee = Math.round(amount * 0.029 + 30); // 2.9% + 30¢

    // Подвійний запис: Дебет активів (PSP), Кредит доходів (Sales)
    this.ledger.push(
      { accountId: "1010-PSP-CLEARING", debitCents: amount, creditCents: 0 },
      { accountId: "4010-SALES-REVENUE", debitCents: 0, creditCents: amount },
      // Проводка комісії шлюзу
      { accountId: "5010-GATEWAY-EXPENSE", debitCents: estimatedFee, creditCents: 0 },
      { accountId: "1010-PSP-CLEARING", debitCents: 0, creditCents: estimatedFee }
    );

    this.processedEventIds.add(eventId);
    return { status: "PROCESSED" };
  }

  getOrder(orderId: string): OrderRecord | undefined {
    return this.orders.get(orderId);
  }

  getLedgerBalance(accountId: string): number {
    return this.ledger
      .filter((l) => l.accountId === accountId)
      .reduce((acc, l) => acc + l.debitCents - l.creditCents, 0);
  }
}
