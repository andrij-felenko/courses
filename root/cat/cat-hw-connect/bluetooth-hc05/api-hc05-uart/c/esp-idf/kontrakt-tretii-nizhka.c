#define PIN_STATE GPIO_NUM_7        // STATE модуля → цей вхід

void state_watch_task(void *arg) {
    const gpio_config_t io = {
        .pin_bit_mask = 1ULL << PIN_STATE,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,   // без модуля вхід тримається в 0
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    bool was = false;
    for (;;) {
        bool now = gpio_get_level(PIN_STATE);   // 1 = є з'єднання, 0 = немає
        if (!was && now) ESP_LOGI(TAG, "З'єднання встановлено.");   // 0→1
        if (was && !now) ESP_LOGW(TAG, "Зв'язок втрачено.");        // 1→0
        was = now;
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
