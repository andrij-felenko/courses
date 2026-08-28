// ts
interface OrderPlacedEventV2 {
  eventId: string;
  orderId: string;
  amount: number;
  taxIdentifier?: string; // Optional field for zero-downtime evolution
}

class OutboxPublisher {
  async saveOrderWithOutbox(orderId: string, amount: number, taxId?: string): Promise<void> {
    console.log(`[DB Tx] Saving Order ${orderId} and writing Outbox event...`);
    // Atomically written in single DB transaction
  }
}

class TolerantBillingConsumer {
  private processedEvents = new Set<string>();

  handleEvent(event: OrderPlacedEventV2): void {
    if (this.processedEvents.has(event.eventId)) {
      console.log(`[TS Consumer] Duplicate event ${event.eventId} skipped.`);
      return;
    }

    console.log(`[TS Consumer] Handling Order=${event.orderId}, Amount=${event.amount}`);
    if (event.taxIdentifier) {
      console.log(`  -> Processing V2 with Tax ID: ${event.taxIdentifier}`);
    } else {
      console.log(`  -> Processing V1 fallback logic (no tax ID)`);
    }

    this.processedEvents.add(event.eventId);
  }
}

// Execution test
const publisher = new OutboxPublisher();
const consumer = new TolerantBillingConsumer();

publisher.saveOrderWithOutbox("ORD-3001", 89.90);
consumer.handleEvent({ eventId: "E-1", orderId: "ORD-3001", amount: 89.90 });
consumer.handleEvent({ eventId: "E-1", orderId: "ORD-3001", amount: 89.90 });
