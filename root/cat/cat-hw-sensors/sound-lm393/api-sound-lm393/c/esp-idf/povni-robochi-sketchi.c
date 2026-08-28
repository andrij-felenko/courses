/* Звуковий давач на LM393 → ESP32, чистий ESP-IDF.
   DO давача на GPIO4, світлодіод на GPIO2.
   ISR живе в IRAM (IRAM_ATTR); подія їде в чергу FreeRTOS. */

#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

#define SOUND     GPIO_NUM_4
#define LED       GPIO_NUM_2
#define WINDOW_US 150000LL                 // вікно дебаунсу: 150 мс у мкс

static const char *TAG = "sound";
static QueueHandle_t evt_q;
static volatile int64_t lastHit = 0;

static void IRAM_ATTR on_sound(void *arg) {     // ISR: відсів і одна подія в чергу
    int64_t t = esp_timer_get_time();
    if (t - lastHit > WINDOW_US) {              // торохтіння того ж плеску — геть
        lastHit = t;
        uint32_t one = 1;
        xQueueSendFromISR(evt_q, &one, NULL);   // черга замість спільних змінних
    }
}

static void blink_task(void *arg) {             // уся «повільна» робота — тут
    uint32_t one, count = 0;
    while (1) {
        if (xQueueReceive(evt_q, &one, portMAX_DELAY) == pdTRUE) {
            gpio_set_level(LED, 1);
            ESP_LOGI(TAG, "плеск #%lu", (unsigned long)++count);
            vTaskDelay(pdMS_TO_TICKS(30));      // коротке блимання
            gpio_set_level(LED, 0);
        }
    }
}

void app_main(void) {
    gpio_config_t in = { .pin_bit_mask = 1ULL << SOUND, .mode = GPIO_MODE_INPUT,
                         .pull_up_en   = GPIO_PULLUP_DISABLE,
                         .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type    = GPIO_INTR_NEGEDGE };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));

    evt_q = xQueueCreate(8, sizeof(uint32_t));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    ESP_ERROR_CHECK(gpio_isr_handler_add(SOUND, on_sound, NULL));

    xTaskCreate(blink_task, "blink", 3072, NULL, 5, NULL);
    ESP_LOGI(TAG, "готово. плесніть у долоні.");
}
