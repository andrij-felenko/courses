/* ESP-IDF: Негативне керування симістором через апаратний gptimer */
#include "freertos/FreeRTOS.h"
#include "driver/gpio.h"
#include "driver/gptimer.h"
#include "esp_rom_sys.h"

#define TRIAC_GPIO            GPIO_NUM_18
#define ZERO_CROSS_GPIO       GPIO_NUM_19

static gptimer_handle_t phase_timer = NULL;
static volatile uint64_t phase_delay_us = 4000; // 40% зріз фази

/* ISR переходу через нуль мережі */
static void IRAM_ATTR zero_cross_isr(void* arg) {
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = phase_delay_us,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(phase_timer, &alarm_config);
    gptimer_set_raw_count(phase_timer, 0);
    gptimer_start(phase_timer);
}

/* ISR фазового таймера: генерація негативної пачки */
static bool IRAM_ATTR on_phase_timer_alarm(gptimer_handle_t timer, 
                                          const gptimer_alarm_event_data_t *edata, 
                                          void *user_data) {
    gptimer_stop(timer);
    
    // Формуємо пачку від'ємних імпульсів (активний LOW)
    for (int i = 0; i < 15; i++) {
        gpio_set_level(TRIAC_GPIO, 0); // Активний затвор: Q-II / Q-III
        esp_rom_delay_us(12);
        gpio_set_level(TRIAC_GPIO, 1); // Закрито
        esp_rom_delay_us(28);
    }
    return false;
}

void app_main(void) {
    // Налаштування GPIO затвора
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TRIAC_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&io_conf);
    gpio_set_level(TRIAC_GPIO, 1); // Початковий стан: закрито (V_G = VCC)

    // Ініціалізація gptimer
    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1000000, // 1 МГц = 1 мкс на тік
    };
    gptimer_new_timer(&timer_config, &phase_timer);

    gptimer_event_callbacks_t cbs = {
        .on_alarm = on_phase_timer_alarm,
    };
    gptimer_register_event_callbacks(phase_timer, &cbs, NULL);
    gptimer_enable(phase_timer);
}
