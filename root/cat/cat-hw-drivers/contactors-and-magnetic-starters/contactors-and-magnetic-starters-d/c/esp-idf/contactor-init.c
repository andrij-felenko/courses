// Керування силовим контактором через транзисторний/релейний драйвер у C (ESP-IDF)
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define CONTACTOR_COIL_GPIO  GPIO_NUM_18
#define INTERLOCK_SENSE_GPIO GPIO_NUM_19
#define MIN_SWITCH_PAUSE_MS  1000

static TickType_t last_toggle_time = 0;

void contactor_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << CONTACTOR_COIL_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
    };
    gpio_config(&io_conf);
}

bool set_contactor_state(bool enable) {
    TickType_t now = xTaskGetTickCount();
    // Захисна пауза між комутаціями для запобігання перегріву дугогасної камери
    if ((now - last_toggle_time) * portTICK_PERIOD_MS < MIN_SWITCH_PAUSE_MS) {
        printf("Помилка: Занадто часте перемикання контактора!\n");
        return false;
    }
    
    gpio_set_level(CONTACTOR_COIL_GPIO, enable ? 1 : 0);
    last_toggle_time = now;
    printf("Котушка контактора: %s\n", enable ? "УВІМКНЕНО" : "ВИМКНЕНО");
    return true;
}
