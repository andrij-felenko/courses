// Викликаємо з повільної петлі, коли є зв'язок і в черзі щось є.
static void evq_flush(void) {
    while (g_evq.count > 0) {
        event_t *e = &g_evq.buf[g_evq.tail];

        char topic[64];
        snprintf(topic, sizeof topic,
                 "home/livingroom/thermostat/event/%u", e->seq);

        char msg[80];
        snprintf(msg, sizeof msg,
                 "{\"seq\":%u,\"type\":%u,\"ts\":%u,\"data\":\"%.*s\"}",
                 e->seq, e->type, e->ts, e->len, e->payload);

        // QoS 1: publish поверне успіх лише коли надіслано в мережу;
        // тверде підтвердження — асинхронний PUBACK (див. on_puback нижче).
        int rc = mqtt_publish(topic, msg, /*qos*/1, /*retain*/0);
        if (rc < 0) {
            // Не змогли навіть покласти в мережу (зв'язок знову впав) —
            // лишаємо все як є: tail не рушив, подія чекає далі.
            break;
        }
        // НЕ зсуваємо tail тут! Чекаємо PUBACK — інакше загубимо
        // подію, якщо PUBLISH пішов, а мережа впала до підтвердження.
        break;   // за раз відсилаємо одну; PUBACK штовхне наступну
    }
}
