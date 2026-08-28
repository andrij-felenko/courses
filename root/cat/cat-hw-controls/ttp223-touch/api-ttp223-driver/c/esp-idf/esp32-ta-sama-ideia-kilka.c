#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#define PIN_TOUCH  GPIO_NUM_4                 // звичайний GPIO, не strapping-нога
static const char   *TAG = "ttp223";
static QueueHandle_t touch_q;

// На ESP32 ISR має лежати в IRAM → атрибут IRAM_ATTR обов'язковий
static void IRAM_ATTR on_touch(void *arg) {
    uint32_t ev = 1;
    xQueueSendFromISR(touch_q, &ev, NULL);    // лише передати факт — і вийти
}

void app_main(void) {
    touch_q = xQueueCreate(8, sizeof(uint32_t));

    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_TOUCH,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,  // двотактний вихід → без підтяжки
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_POSEDGE,    // передній фронт = активний у 1
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));   // спільний диспетчер GPIO-ISR
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_TOUCH, on_touch, NULL));

    uint32_t ev, count = 0;
    while (1) {
        // задача спить на черзі, поки не прийде дотик: ядро вільне для Wi-Fi тощо
        if (xQueueReceive(touch_q, &ev, portMAX_DELAY) == pdTRUE)
            ESP_LOGI(TAG, "дотиків: %u", (unsigned)++count);
    }
}
