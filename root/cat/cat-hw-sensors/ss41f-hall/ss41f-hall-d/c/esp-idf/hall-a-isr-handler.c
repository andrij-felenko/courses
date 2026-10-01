#include "driver/gpio.h"

#define HALL_A_PIN GPIO_NUM_4
#define HALL_B_PIN GPIO_NUM_5
static volatile int32_t encoder_position = 0;

static void IRAM_ATTR hall_a_isr_handler(void* arg) {
    int state_a = gpio_get_level(HALL_A_PIN);
    int state_b = gpio_get_level(HALL_B_PIN);
    if (state_a == state_b) {
        encoder_position++;
    } else {
        encoder_position--;
    }
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << HALL_A_PIN) | (1ULL << HALL_B_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    gpio_config(&io_conf);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(HALL_A_PIN, hall_a_isr_handler, NULL);
}
