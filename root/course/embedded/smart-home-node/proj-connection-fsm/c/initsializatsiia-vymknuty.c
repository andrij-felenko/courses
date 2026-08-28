static void net_init(void) {
    esp_mqtt_client_config_t cfg = {
        .broker.address.uri = "mqtt://192.168.1.10:1883",

        // 1. ВИМИКАЄМО вбудований авто-реконект — перепідключенням керує НАШ автомат.
        .network.disable_auto_reconnect = true,
        .network.timeout_ms             = CONNECT_TIMEOUT_MS,

        // 2. ЗАПОВІТ (Last Will): брокер сам напише offline, якщо ми раптово зникнемо.
        .session.last_will.topic  = "home/livingroom/thermostat/status",
        .session.last_will.msg    = "offline",
        .session.last_will.qos    = 1,
        .session.last_will.retain = 1,
        .session.keepalive        = 60,   // пінг раз на ~30 с; обрив помітний за ~90 с
    };

    g_client = esp_mqtt_client_init(&cfg);
    esp_mqtt_client_register_event(g_client, MQTT_EVENT_ANY,
                                   mqtt_event_handler, NULL);
    esp_mqtt_client_start(g_client);      // запускає фонове завдання клієнта
    // Стан лишається NET_OFFLINE; перше під'єднання ініціює net_step(),
    // щойно wifi_is_connected() поверне true.
}
