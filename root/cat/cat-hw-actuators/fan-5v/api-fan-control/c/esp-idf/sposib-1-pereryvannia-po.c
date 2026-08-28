// ESP-IDF 5.x: підрахунок обертів через GPIO-переривання
#include <inttypes.h>
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TACH_GPIO  GPIO_NUM_27
static const char *TAG = "fan";

static volatile uint32_t tach_edges = 0;     // лічильник фронтів — його чіпає ISR
static portMUX_TYPE tach_mux = portMUX_INITIALIZER_UNLOCKED;

static void IRAM_ATTR tach_isr(void *arg) {  // ISR має жити в IRAM
    tach_edges++;                            // тільки інкремент — нічого важкого в ISR
}

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << TACH_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,      // тахо це відкритий колектор
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_POSEDGE,       // висхідний фронт
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    ESP_ERROR_CHECK(gpio_isr_handler_add(TACH_GPIO, tach_isr, NULL));

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));         // раз на секунду
        portENTER_CRITICAL(&tach_mux);           // атомарно зняти й скинути
        uint32_t edges = tach_edges;
        tach_edges = 0;
        portEXIT_CRITICAL(&tach_mux);

        uint32_t rpm = (edges / 2) * 60;         // ÷2 (2 імпульси/оберт) ×60
        ESP_LOGI(TAG, "TACH: %" PRIu32 " імп/с  ->  %" PRIu32 " об/хв", edges, rpm);
    }
}
