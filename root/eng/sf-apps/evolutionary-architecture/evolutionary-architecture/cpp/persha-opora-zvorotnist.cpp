// ЗІ ШВОМ: логіка знає тільки порт, черга — за адаптером
struct EventBus {                              // порт: контракт без черги
    virtual void publish(const std::string& topic,
                         const std::string& payload) = 0;
    virtual ~EventBus() = default;
};

void publish_order(EventBus& bus, const Order& o) {
    bus.publish("orders", serialize(o));       // жодного сліду Kafka
}

// Конкретна черга живе в ОДНОМУ місці — в адаптері:
struct KafkaBus : EventBus { /* rdkafka саме тут */ };
// Завтра RabbitMQ чи хмарна черга — новий адаптер, publish_order не міняється.
