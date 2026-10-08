#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/gptimer.h"

#define ZERO_CROSS_GPIO  GPIO_NUM_4
#define TRIAC_GATE_GPIO  GPIO_NUM_5

static gptimer_handle_t g_timer = NULL;
static volatile uint32_t g_delay_us = 5000; // 50% потужності (5 мс)

// Переривання від детектора переходу через нуль
static void IRAM_ATTR zero_cross_isr_handler(void* arg) {
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = g_delay_us,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_stop(g_timer);
    gptimer_set_raw_count(g_timer, 0);
    gptimer_set_alarm_action(g_timer, &alarm_config);
    gptimer_start(g_timer);
}

// Спрацьовування таймера затримки фазового кута
static bool IRAM_ATTR timer_on_alarm_cb(gptimer_handle_t timer, 
                                        const gptimer_alarm_event_data_t *edata, 
                                        void *user_ctx) {
    // Подаємо короткий імпульс 30 мкс на вхідний світлодіод MOC3021
    gpio_set_level(TRIAC_GATE_GPIO, 1);
    esp_rom_delay_us(30);
    gpio_set_level(TRIAC_GATE_GPIO, 0);
    return false;
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TRIAC_GATE_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = 0,
        .pull_up_en = 0,
    };
    gpio_config(&io_conf);

    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1000000, // 1 МГц (1 крок = 1 мкс)
    };
    gptimer_new_timer(&timer_config, &g_timer);

    gptimer_event_callbacks_t cbs = {
        .on_alarm = timer_on_alarm_cb,
    };
    gptimer_register_event_callbacks(g_timer, &cbs, NULL);
    gptimer_enable(g_timer);

    gpio_set_intr_type(ZERO_CROSS_GPIO, GPIO_INTR_POSEDGE);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(ZERO_CROSS_GPIO, zero_cross_isr_handler, NULL);
}
