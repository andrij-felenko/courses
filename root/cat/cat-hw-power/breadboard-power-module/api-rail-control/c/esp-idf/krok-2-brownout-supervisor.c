/* ============================================================================
   krok-2-brownout-supervisor.c — ESP-IDF: задача супервізора Brown-out
   ========================================================================== */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "MB102_SUPERVISOR";

#define GPIO_LOAD_GATE       GPIO_NUM_18
#define V_WARN_THRESHOLD_MV  4650
#define V_RECOVERY_MV        4800

extern uint32_t read_rail_mv(void);

static void emergency_shed_load(void) {
    gpio_set_level(GPIO_LOAD_GATE, 1); // Закрити P-MOSFET ключ (вимкнути навантаження)
    ESP_LOGW(TAG, "УВАГА: Небезпечне просідання напруги MB102! Навантаження аварійно відключено!");
}

static void restore_load(void) {
    gpio_set_level(GPIO_LOAD_GATE, 0); // Відкрити ключ назад
    ESP_LOGI(TAG, "Шина MB102 відновилася. Навантаження підключено.");
}

void supervisor_task(void *pvParameters) {
    bool load_active = true;

    while (1) {
        uint32_t v = read_rail_mv();

        if (load_active && (v < V_WARN_THRESHOLD_MV)) {
            emergency_shed_load();
            load_active = false;
        } else if (!load_active && (v >= V_RECOVERY_MV)) {
            restore_load();
            load_active = true;
        }

        vTaskDelay(pdMS_TO_TICKS(15)); // Контроль кожні 15 мс
    }
}

void init_supervisor_hardware(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_LOAD_GATE),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);
    
    // Старт у безпечному стані (вимкнено)
    gpio_set_level(GPIO_LOAD_GATE, 1);
}
