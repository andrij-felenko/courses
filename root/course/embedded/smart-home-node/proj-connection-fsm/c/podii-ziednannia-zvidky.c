// Реєструємо на MQTT_EVENT_ANY; бібліотека кличе це зі свого завдання.
static void mqtt_event_handler(void *arg, esp_event_base_t base,
                               int32_t event_id, void *event_data) {
    esp_mqtt_event_handle_t e = (esp_mqtt_event_handle_t) event_data;

    switch ((esp_mqtt_event_id_t) event_id) {

    case MQTT_EVENT_CONNECTED:
        // Прийшов CONNACK — брокер прийняв нас. Спроба вдалася.
        g_backoff_ceil = BACKOFF_BASE_MS;  // успіх скидає стелю відкату до базової
        net_goto(NET_ONLINE);
        on_online();                       // підписатися, оголосити online, дослати чергу
        break;

    case MQTT_EVENT_DISCONNECTED:
        // Зв'язок розірвано (обрив, keepalive, брокер зник) — падаємо у відкат.
        // Байдуже, з ONLINE чи з CONNECTING ми прийшли: результат один — BACKOFF.
        net_goto(NET_BACKOFF);
        break;

    case MQTT_EVENT_DATA:
        // Прийшла команда на підписаний топік — віддаємо шар вище.
        on_command(e->topic, e->topic_len, e->data, e->data_len);
        break;

    case MQTT_EVENT_PUBLISHED:
        // PUBACK на наше QoS-1 повідомлення — штовхає чергу подій (див. буфер).
        on_puback(e->msg_id);
        break;

    default:
        break;   // решту подій ігноруємо
    }
}
