type DomainEvent<T = unknown> = {
  eventId: string;    // унікальний id САМЕ ЦЬОГО оголошення (не orderId!)
  type: string;
  payload: T;
};

// маленький помічник збирає конверт і проставляє свіжий id
function makeEvent<T>(type: string, payload: T): DomainEvent<T> {
  return { eventId: crypto.randomUUID(), type, payload };
}
