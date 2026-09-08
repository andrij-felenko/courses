/* ============================================================================
   krok-3-zero-cross-relay.c — ESP-IDF: комутація реле синхронно з нулем напруги
   ========================================================================== */

#include <stdio.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

static const char *TAG = "ZC_RELAY";

#define GPIO_RELAY_PIN          GPIO_NUM_18
#define RELAY_MECHANICAL_LAG_US 6000     // Механічний час спрацьовування якоря ~6 мс
#define AC_HALF_PERIOD_US       10000    // 10 мс для мережі 50 Гц

static SemaphoreHandle_t s_zc_sem = NULL;
static volatile bool     s_target_relay_state = false;

static void IRAM_ATTR on_zero_cross_edge(void *arg) {
    BaseType_t high_task_wakeup = pdFALSE;
    if (s_zc_sem) {
        xSemaphoreGiveFromISR(s_zc_sem, &high_task_wakeup);
        if (high_task_wakeup) {
            portYIELD_FROM_ISR();
        }
    }
}

// Завдання точної синхронізації моменту комутації
static void relay_sync_task(void *pvParameters) {
    while (1) {
        if (xSemaphoreTake(s_zc_sem, portMAX_DELAY) == pdTRUE) {
            // Отримали імпульс нуля фази (Zero-Cross).
            // Щоб контакт зімкнувся точно в наступному нулі (через 10 мс),
            // подаємо напругу на котушку із затримкою: 10 мс - T_якоря (6 мс) = 4 мс.
            uint32_t delay_us = AC_HALF_PERIOD_US - RELAY_MECHANICAL_LAG_US;
            esp_rom_delay_us(delay_us);

            gpio_set_level(GPIO_RELAY_PIN, s_target_relay_state ? 1 : 0);
            ESP_LOGI(TAG, "Реле перемкнено в стан %d у фазовому нулі", s_target_relay_state);
        }
    }
}

void zero_cross_relay_init(void) {
    s_zc_sem = xSemaphoreCreateBinary();

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_RELAY_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
    };
    gpio_config(&io_conf);
    gpio_set_level(GPIO_RELAY_PIN, 0);

    xTaskCreate(relay_sync_task, "zc_relay_task", 2048, NULL, configMAX_PRIORITIES - 1, NULL);
}

void relay_request_state(bool enable) {
    s_target_relay_state = enable;
}
