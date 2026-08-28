/* Внутрішня структура бізнес-домену замовлень */
typedef struct {
    uint32_t order_id;
    uint32_t customer_id;
    uint32_t amount_cents;
    char currency[4];
} OrderPlacedEvent;

/* Адаптер-видавець: Order Service Outbound Adapter */
void order_service_publish_order(MessageBus* bus, uint32_t order_id, uint32_t cust_id, uint32_t cents) {
    OrderPlacedEvent evt;
    evt.order_id = order_id;
    evt.customer_id = cust_id;
    evt.amount_cents = cents;
    strncpy(evt.currency, "UAH", 4);
    
    MessageEnvelope env;
    envelope_init(&env, "orders.created", "", 2 /* schema v2 */);
    
    /* Бінарна серіалізація в корисне навантаження конверта */
    memcpy(env.payload, &evt, sizeof(OrderPlacedEvent));
    env.payload_len = sizeof(OrderPlacedEvent);
    
    printf("\n--> [OrderService] Створено замовлення #%u на суму %u.%02u %s. Публікація в шину...\n",
           order_id, cents / 100, cents % 100, evt.currency);
    bus_publish(bus, &env);
}

/* Адаптер-споживач 1: Billing Service Inbound Handler */
void billing_service_handler(const MessageEnvelope* env, void* ctx) {
    (void)ctx;
    if (env->payload_len != sizeof(OrderPlacedEvent)) return;
    
    const OrderPlacedEvent* evt = (const OrderPlacedEvent*)env->payload;
    printf("  [BillingService] ОТРИМАНО подію: Списання коштів за замовленням #%u: %u.%02u %s (Trace: %s)\n",
           evt->order_id, evt->amount_cents / 100, evt->amount_cents % 100, evt->currency, env->traceparent);
}

/* Адаптер-споживач 2: Notification Service Inbound Handler */
void notification_service_handler(const MessageEnvelope* env, void* ctx) {
    (void)ctx;
    if (env->payload_len != sizeof(OrderPlacedEvent)) return;
    
    const OrderPlacedEvent* evt = (const OrderPlacedEvent*)env->payload;
    printf("  [NotificationService] ОТРИМАНО подію: Відправка SMS клієнту #%u: Замовлення #%u підтверджено\n",
           evt->customer_id, evt->order_id);
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ РОБОТИ ШИНИ ПОВІДОМЛЕНЬ (C) ===\n");
    
    MessageBus bus;
    bus_init(&bus);
    
    /* Налаштування конвеєра перехоплювачів */
    uint32_t min_version = 2;
    DedupCache dedup_cache = {.count = 0};
    
    bus_add_interceptor(&bus, schema_validator_interceptor, &min_version);
    bus_add_interceptor(&bus, tracing_logger_interceptor, NULL);
    bus_add_interceptor(&bus, dedup_interceptor, &dedup_cache);
    
    /* Реєстрація підписок сервісів */
    bus_subscribe(&bus, "orders.*", billing_service_handler, NULL);
    bus_subscribe(&bus, "orders.created", notification_service_handler, NULL);
    
    /* Сценарій 1: Успішна публікація замовлення */
    order_service_publish_order(&bus, 4010, 77, 150000);
    
    /* Сценарій 2: Відхилення повідомлення із застарілою схемою v1 */
    printf("\n--> [LegacyProducer] Спроба публікації повідомлення за схемою v1...\n");
    MessageEnvelope old_env;
    envelope_init(&old_env, "orders.created", "corr_old", 1 /* v1 */);
    bus_publish(&bus, &old_env);
    
    return 0;
}
