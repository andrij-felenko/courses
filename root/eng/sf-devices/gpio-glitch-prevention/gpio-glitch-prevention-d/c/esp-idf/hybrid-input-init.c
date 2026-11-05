#include <stdio.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SENSOR_GPIO_PIN   GPIO_NUM_5
#define STABLE_SAMPLES    4
#define SAMPLE_PERIOD_MS  10

typedef struct {
    gpio_num_t pin;
    bool last_stable_state;
    uint8_t sample_history;
} HybridInput_t;

void hybrid_input_init(HybridInput_t *dev, gpio_num_t gpio_num)
{
    dev->pin = gpio_num;
    dev->last_stable_state = false;
    dev->sample_history = 0xFF;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << gpio_num),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}

bool hybrid_input_update(HybridInput_t *dev)
{
    // Зчитання поточного цифрового стану піна після вбудованого тригера Шмітта
    int raw_level = gpio_get_level(dev->pin);
    
    // Оновлення зсувного регістра історії відліків
    dev->sample_history = (dev->sample_history << 1) | (raw_level & 0x01);

    // Мажоритарна перевірка: 4 послідовних одиниці або 4 послідовних нулі
    uint8_t mask = (1 << STABLE_SAMPLES) - 1;
    uint8_t current_pattern = dev->sample_history & mask;

    if (current_pattern == mask) {
        dev->last_stable_state = true;
    } else if (current_pattern == 0x00) {
        dev->last_stable_state = false;
    }

    return dev->last_stable_state;
}
