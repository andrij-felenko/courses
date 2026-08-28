// ЗІ ШВОМ: логіка знає тільки порт, черга — за адаптером
package orders

// EventBus — порт: контракт без черги.
type EventBus interface {
	Publish(topic string, payload []byte) error
}

func PublishOrder(bus EventBus, o Order) error {
	return bus.Publish("orders", serialize(o)) // жодного сліду Kafka
}

// Конкретна черга живе в ОДНОМУ місці — в адаптері:
type KafkaBus struct{ /* kafka.Writer саме тут */ }

func (b *KafkaBus) Publish(topic string, payload []byte) error { /* ... */ }

// Завтра RabbitMQ чи хмарна черга — новий адаптер, PublishOrder не міняється.
