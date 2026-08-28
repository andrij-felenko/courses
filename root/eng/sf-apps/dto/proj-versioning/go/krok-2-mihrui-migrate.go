// Фаза migrate: сервер кладе В ОБИДВА поля, поки живі читачі обох поколінь.
func ToWire(order DomainOrder) RawOrder {
	id := StableCustomerID(order.Customer) // канонічний ключ клієнта
	return RawOrder{
		ID:            order.ID,
		Total:         order.Total(), // ПРАВИЛО домену, не сире поле
		CustomerID:    id,            // нове покоління читає це
		CustomerEmail: EmailFor(id),  // старе покоління ще читає це
	}
}
