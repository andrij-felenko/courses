#include "driver/gpio.h"
#include "esp_log.h"

#define PIN_STATE GPIO_NUM_4        // STATE модуля → цей вхід МК

static const char *TAG = "car";
static bool wasConnected = false;

static void stateInit(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_STATE,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,   // поки модуль мовчить, вхід не «висить»
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
}

static void statePoll(void) {                   // виклик у головному циклі задачі
    bool connected = gpio_get_level(PIN_STATE); // 1 = є з'єднання, 0 = немає

    if (wasConnected && !connected) {
        // зв'язок ЩОЙНО обірвався — аварійний стоп
        applyDrive(0, 0);
        ESP_LOGW(TAG, "Зв'язок втрачено — мотори зупинено.");
    }
    wasConnected = connected;
}
