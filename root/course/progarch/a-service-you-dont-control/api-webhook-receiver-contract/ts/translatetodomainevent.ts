// Канонічна доменна подія нашої системи
export interface DomainPaymentCompletedEvent {
  eventId: string;
  orderId: string;
  paidAmount: number; // Нормалізовано: 1500.00 UAH
  currency: string;
  externalTransactionId: string;
  occurredAt: Date;
}

// Функція-адаптер антикорупційного шару
export function translateToDomainEvent(rawEvent: any): DomainPaymentCompletedEvent {
  const intent = rawEvent.data?.object;
  if (!intent) {
    throw new Error('CORRUPTED_WEBHOOK_PAYLOAD');
  }

  return {
    eventId: rawEvent.id,
    orderId: intent.metadata?.order_id || intent.id,
    paidAmount: intent.amount / 100, // Конвертація з копійок у гривні
    currency: intent.currency.toUpperCase(),
    externalTransactionId: intent.id,
    occurredAt: new Date(rawEvent.created * 1000)
  };
}
