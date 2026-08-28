interface OrderEvent {
  eventId: string;
  orderId: string;
  userId: string;
  orderState: string;
  currency: string;
  totalAmountCents: number;
  taxAmountCents: number;
  itemsCount: number;
  createdAt: string;
}

interface DlqEnvelope {
  dlqId: string;
  failedAt: string;
  contractVersion: string;
  errorReason: string;
  rawPayload: string;
}

class DataContractValidator {
  private readonly validStates = new Set(["PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"]);

  constructor(public readonly contractVersion: string) {}

  public validate(ev: Partial<OrderEvent>): { valid: boolean; error?: string } {
    if (!ev.eventId || !ev.orderId || !ev.userId) {
      return { valid: false, error: "Відсутній обов'язковий ідентифікатор" };
    }
    if (typeof ev.totalAmountCents !== "number" || ev.totalAmountCents < 0) {
      return { valid: false, error: "totalAmountCents має бути невід'ємним числом" };
    }
    if (typeof ev.itemsCount !== "number" || ev.itemsCount <= 0 || ev.itemsCount > 500) {
      return { valid: false, error: "itemsCount має бути числом у межах [1, 500]" };
    }
    if (!ev.orderState || !this.validStates.has(ev.orderState)) {
      return { valid: false, error: `Недопустимий статус orderState: ${ev.orderState}` };
    }
    if (!ev.currency || ev.currency.length !== 3) {
      return { valid: false, error: "Код currency має складатись з 3 символів" };
    }
    if ((ev.taxAmountCents ?? 0) > ev.totalAmountCents) {
      return { valid: false, error: "taxAmountCents перевищує totalAmountCents" };
    }
    return { valid: true };
  }
}

class IngestionGateway {
  public dwhSink: OrderEvent[] = [];
  public dlqSink: DlqEnvelope[] = [];

  constructor(private validator: DataContractValidator) {}

  public process(rawJson: string): void {
    try {
      const parsed = JSON.parse(rawJson) as Partial<OrderEvent>;
      const check = this.validator.validate(parsed);
      if (check.valid) {
        this.dwhSink.push(parsed as OrderEvent);
      } else {
        this.dlqSink.push({
          dlqId: "uuid-dlq-sample",
          failedAt: new Date().toISOString(),
          contractVersion: this.validator.contractVersion,
          errorReason: check.error || "Validation error",
          rawPayload: rawJson,
        });
      }
    } catch (err) {
      this.dlqSink.push({
        dlqId: "uuid-dlq-parse-err",
        failedAt: new Date().toISOString(),
        contractVersion: this.validator.contractVersion,
        errorReason: "JSON parse error",
        rawPayload: rawJson,
      });
    }
  }
}
