#include "driver/gpio.h"
#include "driver/gptimer.h"

static volatile uint32_t delay_us = 5000;
static gptimer_handle_t timer = NULL;

// Переривання від детектора нуля скидає та запускає таймер
static void IRAM_ATTR zero_cross_isr(void *arg) {
    gptimer_set_raw_count(timer, 0);
    gptimer_start(timer);
}

// Спрацьовування таймера подає імпульс відмикання на симістор
static bool IRAM_ATTR timer_on_alarm(gptimer_handle_t timer, const gptimer_alarm_event_data_t *edata, void *user_ctx) {
    gpio_set_level(GPIO_NUM_18, 1);
    esp_rom_delay_us(30);
    gpio_set_level(GPIO_NUM_18, 0);
    gptimer_stop(timer);
    return false;
}
