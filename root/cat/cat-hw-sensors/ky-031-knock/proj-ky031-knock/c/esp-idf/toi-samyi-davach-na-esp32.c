#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4
#define LED         GPIO_NUM_2
#define LOCKOUT_US  60000

static const char *TAG = "knock";
static QueueHandle_t q;               // ISR → задача, без спільних змінних

/* IRAM_ATTR — той самий припис, що й у скетчі: обробник у внутрішній RAM */
static void IRAM_ATTR on_knock(void *arg) {
    int64_t t = esp_timer_get_time();      // годинник в ISR тут іде — мітимо одразу
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR(q, &t, &woken);      // ISR лише кидає мітку в чергу
    if (woken) portYIELD_FROM_ISR();
}

static void knock_task(void *arg) {
    int64_t t, last = 0;
    unsigned count = 0;
    while (1) {
        if (xQueueReceive(q, &t, pdMS_TO_TICKS(30)) == pdTRUE) {
            if (t - last > LOCKOUT_US) {   // поза глухим вікном — правдивий стук
                last = t;
                count++;
                gpio_set_level(LED, 1);
                ESP_LOGI(TAG, "стук #%u", count);
            }
        } else {
            gpio_set_level(LED, 0);        // 30 мс тиші — гасимо світлодіод
        }
    }
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));
    q = xQueueCreate(8, sizeof(int64_t));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));
    xTaskCreate(knock_task, "knock", 3072, NULL, 5, NULL);
}
