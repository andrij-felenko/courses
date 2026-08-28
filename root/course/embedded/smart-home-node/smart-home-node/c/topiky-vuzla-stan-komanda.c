// Викликається бібліотекою, коли на підписаний топік прийшло повідомлення.
// topic/data — НЕ нуль-терміновані C-рядки, а шматки з довжиною (пастка ESP-MQTT).
static void on_command(const char *topic, int topic_len,
                       const char *data,  int data_len) {
    // Нас цікавить лише топік команди зміни порога
    if (topic_len == strlen("home/livingroom/thermostat/set") &&
        strncmp(topic, "home/livingroom/thermostat/set", topic_len) == 0) {
        char buf[16];
        int n = data_len < 15 ? data_len : 15;
        memcpy(buf, data, n); buf[n] = '\0';   // робимо з шматка справжній рядок
        float v = strtof(buf, NULL);
        if (v > 5.0f && v < 35.0f) {           // перевіряємо межі — чужому не довіряй
            g_setpoint = v;
            nvs_save_float("setpoint", v);      // запам'ятати, щоб пережити перезавантаження
        }
    }
}
