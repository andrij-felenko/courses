/* Структура канонічної події замовлення */
struct OrderPlacedEvent {
    uint32_t order_id{0};
    uint32_t customer_id{0};
    uint32_t amount_cents{0};
    char currency[4]{"UAH"};
};

/* Адаптер видавця: Order Service */
void publish_order(MessageBus& bus, uint32_t order_id, uint32_t cust_id, uint32_t cents) {
    OrderPlacedEvent evt{order_id, cust_id, cents, "UAH"};
    
    auto env = MessageEnvelope::create("orders.created", "", 2 /* v2 */);
    
    std::span<const uint8_t> bytes(reinterpret_cast<const uint8_t*>(&evt), sizeof(evt));
    env.set_payload(bytes);
    
    std::cout << std::format("\n--> [OrderService] Створено замовлення #{} на суму {}.{:02d} {}. Публікація в шину...\n",
                             order_id, cents / 100, cents % 100, evt.currency);
    bus.publish(env);
}

int main() {
    std::cout << "=== ДЕМОНСТРАЦІЯ РОБОТИ ШИНИ ПОВІДОМЛЕНЬ (C++) ===\n";

    MessageBus bus;

    /* Реєстрація перехоплювачів */
    bus.add_interceptor(make_schema_validator(2));
    bus.add_interceptor(make_tracing_logger());
    
    DedupInterceptor dedup;
    bus.add_interceptor([&dedup](MessageEnvelope& env) {
        return dedup(env);
    });

    /* Підписка сервісу білінгу на всі події orders.* */
    bus.subscribe("orders.*", [](const MessageEnvelope& env) {
        if (env.payload.size() == sizeof(OrderPlacedEvent)) {
            const auto* evt = reinterpret_cast<const OrderPlacedEvent*>(env.payload.data());
            std::cout << std::format("  [BillingService] ОТРИМАНО: Списання коштів за замовленням #{}: {}.{:02d} {} (Trace: {})\n",
                                     evt->order_id, evt->amount_cents / 100, evt->amount_cents % 100, 
                                     evt->currency, env.traceparent);
        }
    });

    /* Підписка сервісу сповіщень на точну тему orders.created */
    bus.subscribe("orders.created", [](const MessageEnvelope& env) {
        if (env.payload.size() == sizeof(OrderPlacedEvent)) {
            const auto* evt = reinterpret_cast<const OrderPlacedEvent*>(env.payload.data());
            std::cout << std::format("  [NotificationService] ОТРИМАНО: SMS клієнту #{}: Замовлення #{} підтверджено\n",
                                     evt->customer_id, evt->order_id);
        }
    });

    /* Сценарій 1: Успішна публікація події */
    publish_order(bus, 4010, 77, 150000);

    /* Сценарій 2: Відхилення застарілої схеми v1 */
    std::cout << "\n--> [LegacyProducer] Спроба публікації повідомлення за схемою v1...\n";
    auto old_env = MessageEnvelope::create("orders.created", "corr_old", 1 /* v1 */);
    bus.publish(old_env);

    return 0;
}
