#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#define PIN_SHOCK    GPIO_NUM_4      // звичайна GPIO з підтяжкою
#define DEBOUNCE_US  60000           // 60 мс у мікросекундах

static const char *TAG = "ky002";
static QueueHandle_t g_q;            // черга міток часу з ISR у задачу

// ISR обов'язково в IRAM і максимально коротка: лише кинути мітку в чергу.
static void IRAM_ATTR shock_isr(void *arg) {
    int64_t t = esp_timer_get_time();
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR(g_q, &t, &woken);      // саме ...FromISR, не xQueueSend
    if (woken) portYIELD_FROM_ISR();
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_SHOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    vTaskDelay(pdMS_TO_TICKS(50));

    int idle = gpio_get_level(PIN_SHOCK);
    ESP_LOGI(TAG, "Рівень спокою = %s", idle ? "HIGH (pull-up)" : "LOW (pull-down)");

    // Той самий принцип автополярності, що й в Arduino-ядрі:
    ESP_ERROR_CHECK(gpio_set_intr_type(PIN_SHOCK,
                    idle ? GPIO_INTR_NEGEDGE : GPIO_INTR_POSEDGE));

    g_q = xQueueCreate(32, sizeof(int64_t));  // чергу створюємо ДО вмикання ISR
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_SHOCK, shock_isr, NULL));
    ESP_LOGI(TAG, "Готовий. Струсіть давач.");

    int64_t edgeUs, lastShockUs = 0;
    uint32_t shocks = 0;
    while (1) {
        // Задача СПИТЬ, доки ISR не покладе мітку, — жодного опитування ноги.
        if (xQueueReceive(g_q, &edgeUs, portMAX_DELAY) != pdTRUE) continue;
        if (edgeUs - lastShockUs < DEBOUNCE_US) continue;   // відскок пружини
        lastShockUs = edgeUs;
        ESP_LOGI(TAG, "СТРУС #%u", (unsigned)(++shocks));
    }
    // інші задачі — Wi-Fi, дисплей, давачі — увесь час вільні
}
