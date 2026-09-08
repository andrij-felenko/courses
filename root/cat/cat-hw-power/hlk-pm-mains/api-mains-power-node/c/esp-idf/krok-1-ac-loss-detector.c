/* ============================================================================
   krok-1-ac-loss-detector.c — ESP-IDF: виявлення зникнення 220 В через оптопару
   ========================================================================== */

#include <stdio.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "MAINS_DETECTOR";

#define GPIO_ZERO_CROSS_IN    GPIO_NUM_4    // Вихід оптопари PC814 (Active Low)
#define AC_LOSS_TIMEOUT_US    15000         // 15 мс (при 50 Гц напівперіод = 10 мс)

static volatile int64_t s_last_pulse_us = 0;
static volatile bool    s_ac_present = false;

// Переривання на кожному переході фази через нуль (100 Гц = кожні 10 мс)
static void IRAM_ATTR zero_cross_isr_handler(void *arg) {
    s_last_pulse_us = esp_timer_get_time();
    s_ac_present = true;
}

void mains_detector_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_ZERO_CROSS_IN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,    // Оптопара підтягує до GND при імпульсі
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_NEGEDGE,       // Спад на виході фототранзистора
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(GPIO_ZERO_CROSS_IN, zero_cross_isr_handler, NULL);

    s_last_pulse_us = esp_timer_get_time();
    ESP_LOGI(TAG, "Детектор мережі 220 В ініціалізовано на GPIO%d", GPIO_ZERO_CROSS_IN);
}

bool mains_is_ac_present(void) {
    int64_t now = esp_timer_get_time();
    if ((now - s_last_pulse_us) > AC_LOSS_TIMEOUT_US) {
        s_ac_present = false;
    }
    return s_ac_present;
}
