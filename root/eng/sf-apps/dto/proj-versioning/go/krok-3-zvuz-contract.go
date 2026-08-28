// Поки готуємось до звуження — рахуємо, чи хтось ще спирається на старе поле.
func ReadCustomer(raw map[string]any) string {
	if id, _ := raw["customer_id"].(string); id != "" {
		return id
	}
	metrics.Increment("order.read.fallback_to_email") // ← хтось ще на старому шляху
	email, _ := raw["customer_email"].(string)
	return DeriveIDFromEmail(email)
}
// Звужувати можна, коли цей лічильник тримає НУЛЬ довше за максимальну
// «затримку» флоту (довше, ніж може прожити найстаріший клієнт без оновлення).
