#include <stdio.h>
#include <string.h>
#include "esp_timer.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define TACHO_GPIO_PIN       GPIO_NUM_18
#define TACHO_SLOTS_PER_REV  4           /* Кількість контрастних міток на диску */
#define TACHO_FILTER_SIZE    8           /* Розмір вікна ковзного усереднення */
#define MIN_PULSE_PERIOD_US  500         /* Апаратний дебаунс: відсікання завад > 2000 Гц */

static const char *TAG = "TCRT_TACHO";

typedef struct {
    volatile int64_t last_pulse_time_us;
    volatile int64_t periods_us[TACHO_FILTER_SIZE];
    volatile uint8_t filter_index;
    volatile uint32_t total_pulse_count;
} tacho_state_t;

static tacho_state_t g_tacho = {0};

/* Обробник зовнішнього переривання від компаратора LM393 (TCRT5000) */
static void IRAM_ATTR tacho_gpio_isr_handler(void *arg) {
    int64_t now_us = esp_timer_get_time();
    int64_t dt_us = now_us - g_tacho.last_pulse_time_us;

    /* Фільтрація оптичного брязкоту та високочастотних завад */
    if (dt_us > MIN_PULSE_PERIOD_US) {
        g_tacho.last_pulse_time_us = now_us;
        g_tacho.periods_us[g_tacho.filter_index] = dt_us;
        g_tacho.filter_index = (g_tacho.filter_index + 1) % TACHO_FILTER_SIZE;
        g_tacho.total_pulse_count++;
    }
}

/* Ініціалізація GPIO та переривання */
esp_err_t tacho_init(gpio_num_t pin) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_NEGEDGE   /* Спад напруги: проходження білої мітки */
    };
    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) return err;

    gpio_install_isr_service(0);
    return gpio_isr_handler_add(pin, tacho_gpio_isr_handler, NULL);
}

/* Розрахунок поточної швидкості у RPM з ковзним усередненням */
float tacho_get_rpm(void) {
    int64_t now_us = esp_timer_get_time();
    
    /* Якщо вал зупинився (немає імпульсів понад 500 мс) */
    if (now_us - g_tacho.last_pulse_time_us > 500000) {
        return 0.0f;
    }

    int64_t sum_period_us = 0;
    for (int i = 0; i < TACHO_FILTER_SIZE; i++) {
        sum_period_us += g_tacho.periods_us[i];
    }
    
    float avg_period_us = (float)sum_period_us / TACHO_FILTER_SIZE;
    if (avg_period_us <= 0.0f) return 0.0f;

    /* RPM = (60 * 10^6 мкс/хв) / (slots * T_avg) */
    return (60.0f * 1000000.0f) / (TACHO_SLOTS_PER_REV * avg_period_us);
}
