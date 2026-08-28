// Поки готуємось до звуження — рахуємо, чи хтось ще спирається на старе поле.
function readCustomer(raw: RawOrder): string {
  if (typeof raw.customer_id === "string" && raw.customer_id) {
    return raw.customer_id;
  }
  metrics.increment("order.read.fallback_to_email");   // ← хтось ще на старому шляху
  return deriveIdFromEmail(raw.customer_email);
}
// Звужувати можна, коли цей лічильник тримає НУЛЬ довше за максимальну
// «затримку» флоту (довше, ніж може прожити найстаріший клієнт без оновлення).
