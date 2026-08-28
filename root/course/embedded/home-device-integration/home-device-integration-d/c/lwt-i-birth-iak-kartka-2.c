// Підписка на birth-топік Home Assistant: коли HA стартує, він кричить сюди.
static void on_mqtt_connected(mqtt_client_t *c) {
    announce_alive();
    announce_to_home_assistant();          // візитівка (з попереднього кроку)
    mqtt_subscribe(c, "homeassistant/status", /*qos=*/1);
}

// Прийшло щось у homeassistant/status — HA щойно ожив і просить рекомендуватися.
static void on_message(const char *topic, const char *payload, int len) {
    if (strcmp(topic, "homeassistant/status") == 0 &&
        len == 6 && memcmp(payload, "online", 6) == 0) {
        announce_to_home_assistant();       // переоголошуємо себе
        publish_current_state();            // і одразу свіже число
    }
}
