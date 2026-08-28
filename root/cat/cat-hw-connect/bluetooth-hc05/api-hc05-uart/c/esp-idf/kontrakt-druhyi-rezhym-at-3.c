static const char *TAG = "hc05";

static const struct { const char *cmd; const char *what; } steps[] = {
    { "AT",                  "перевірка зв'язку" },
    { "AT+NAME=MyBT",        "ім'я модуля" },
    { "AT+PSWD=4726",        "новий PIN (замість 1234)" },
    { "AT+UART=9600,0,0",    "робоча швидкість 9600, 1 стоп-біт, без парності" },
    { "AT+ROLE=0",           "роль: ведений (slave) — чекає вхідне з'єднання [HC-05]" },
};

void configure_module(void) {
    char resp[64];
    for (size_t i = 0; i < sizeof(steps) / sizeof(steps[0]); i++) {
        bool ok = send_at(steps[i].cmd, resp, sizeof(resp), 1000);
        ESP_LOGI(TAG, "%s  →  %s", steps[i].what, resp);   // повний текст відповіді
        if (!ok) {
            ESP_LOGE(TAG, "НЕ OK. Перевір: EN високо? швидкість 38400? \\r\\n?");
            return;                                        // далі немає сенсу
        }
    }
    ESP_LOGI(TAG, "Налаштування завершено. Знеструм і подай живлення без EN.");
}
