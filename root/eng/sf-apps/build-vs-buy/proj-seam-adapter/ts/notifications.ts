// domain/notifications.ts — усе у ВАШИХ термінах. Постачальника тут нема й близько.

export interface Recipient {
  email: string;
  name: string;
  locale: "uk" | "en";     // якою мовою слати — знає домен, не вендор
}

// Подія домену — те, ПРО ЩО сповіщаємо, мовою вашого продукту.
export type DomainEvent =
  | { kind: "order_shipped"; orderId: string; etaMinutes: number }
  | { kind: "courier_near"; orderId: string; minutesAway: number }
  | { kind: "order_delivered"; orderId: string };

// Наслідок спроби — теж доменний: доставлено / варто повторити / марно.
export type NotifyOutcome =
  | { status: "delivered" }
  | { status: "retryable"; reason: string }
  | { status: "rejected"; reason: string };

// Порт: одне гніздо, назване вашою ПОТРЕБОЮ.
export interface Notifier {
  notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome>;
}
