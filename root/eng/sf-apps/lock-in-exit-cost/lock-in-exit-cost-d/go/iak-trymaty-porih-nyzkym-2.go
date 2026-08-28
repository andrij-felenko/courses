// Бізнес-логіка сліпа до вендора — говорить тільки зі швом.
func shipOrder(q MessageQueue, o Order) error {
	return q.Publish("orders", serialize(o))
}

func main() {
	queue, err := NewVendorAQueue("amqp://broker") // вибір вендора — в одному місці
	if err != nil {
		log.Fatal(err)
	}
	// Переїзд на вендора B = замінити цей рядок на NewVendorBQueue
	// і написати новий адаптер. shipOrder не змінюється взагалі.
	_ = queue
}
