/* ============================================================================
   krok-2-isolated-heartbeat.c — ESP-IDF: моніторинг пульсу оптопари (Heartbeat)
   ========================================================================== */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "ISO_HEARTBEAT";

#define GPIO_HEARTBEAT_IN    GPIO_NUM_34  // Вхід від фототранзистора оптопари PC817
#define TIMEOUT_US           60000        // 60 мс без імпульсу = аварія живлення

static volatile int64_t s_last_pulse_time_us = 0;
static volatile bool    s_iso_power_ok = false;

static void IRAM_ATTR heartbeat_isr_handler(void* arg) {
    s_last_pulse_time_us = esp_timer_get_time();
    s_iso_power_ok = true;
}

void init_isolated_heartbeat(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_HEARTBEAT_IN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE, // Підтяжка до 3.3 В первинного боку
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_NEGEDGE,
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(GPIO_HEARTBEAT_IN, heartbeat_isr_handler, NULL);
}

bool is_isolated_power_healthy(void) {
    int64_t now = esp_timer_get_time();
    if ((now - s_last_pulse_time_us) > TIMEOUT_US) {
        s_iso_power_ok = false;
    }
    return s_iso_power_ok;
}
