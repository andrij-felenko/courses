// Викликається, коли MQTT-з'єднання відновлено (подія CONNECTED).
static void on_mqtt_connected(void) {
    g_net_up = true;                    // 1. відкриваємо канал для звітів

    // 2. заново оголошуємо присутність: ми знову живі
    mqtt_publish("home/livingroom/thermostat/status",
                 "online", /*qos*/1, /*retain*/1);

    // 3. і тільки тепер спускаємо з ланцюга накопичену чергу подій
    if (g_evq_overflowed) {
        // Чесно зізнаємося, що дещо загубили через переповнення.
        char note[48];
        snprintf(note, sizeof note, "{\"dropped\":%u}", g_evq_dropped);
        mqtt_publish("home/livingroom/thermostat/event/overflow",
                     note, /*qos*/1, /*retain*/0);
        g_evq_overflowed = false;
        g_evq_dropped = 0;
    }
    evq_flush();                        // штовхаємо першу подію; далі — по PUBACK
}
