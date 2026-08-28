// Бізнес-логіка сліпа до вендора — говорить тільки зі швом.
void ship_order(MessageQueue& q, const Order& o) {
    q.publish("orders", serialize(o));
}

int main() {
    VendorAQueue queue("amqp://broker");  // вибір вендора — в одному рядку
    // Переїзд на вендора B = замінити цей рядок на VendorBQueue
    // і написати новий адаптер. Ship_order не змінюється взагалі.
}
