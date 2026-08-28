// Фаза migrate: сервер кладе В ОБИДВА поля, поки живі читачі обох поколінь.
function toWire(order: DomainOrder): RawOrder {
  const id = stableCustomerId(order.customer);   // канонічний ключ клієнта
  return {
    id: order.id,
    total: order.total(),                        // ПРАВИЛО домену, не сире поле
    customer_id: id,                             // нове покоління читає це
    customer_email: emailFor(id),                // старе покоління ще читає це
  };
}
