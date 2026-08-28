#define SOUND     GPIO_NUM_4
#define WINDOW_US 150000LL                    // вікно дебаунсу: 150 мс у мкс

static const char *TAG = "sound";
static QueueHandle_t evt_q;                   // ISR → задача, без спільних змінних
static volatile int64_t lastHit = 0;

static void IRAM_ATTR on_sound(void *arg) {   // ISR
    int64_t t = esp_timer_get_time();         // мкс від старту; у ISR читати можна
    if (t - lastHit > WINDOW_US) {            // дебаунс прямо в перериванні
        lastHit = t;
        uint32_t one = 1;
        xQueueSendFromISR(evt_q, &one, NULL); // черга сама розбудить задачу
    }
}

void app_main(void) {
    gpio_config_t io = { .pin_bit_mask = 1ULL << SOUND, .mode = GPIO_MODE_INPUT,
                         .pull_up_en   = GPIO_PULLUP_DISABLE,
                         .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type    = GPIO_INTR_NEGEDGE };
    ESP_ERROR_CHECK(gpio_config(&io));
    evt_q = xQueueCreate(8, sizeof(uint32_t));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    ESP_ERROR_CHECK(gpio_isr_handler_add(SOUND, on_sound, NULL));

    uint32_t one, count = 0;
    while (1) {                               // задача спить, поки тихо
        if (xQueueReceive(evt_q, &one, portMAX_DELAY) == pdTRUE)
            ESP_LOGI(TAG, "плеск #%lu", (unsigned long)++count);
    }
}
