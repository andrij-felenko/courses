#include "driver/gpio.h"
#include "esp_attr.h"

#define STO_CHANNEL_1_PIN  GPIO_NUM_18
#define STO_CHANNEL_2_PIN  GPIO_NUM_19
#define INVERTER_GATE_EN   GPIO_NUM_21

// Апаратне переривання аварійної зупинки (STO)
static void IRAM_ATTR sto_isr_handler(void* arg) {
    // Негайно вимикаємо дозволяючий сигнал драйверів затворів MOSFET
    gpio_set_level(INVERTER_GATE_EN, 0);
}

void init_safety_hardware(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << STO_CHANNEL_1_PIN) | (1ULL << STO_CHANNEL_2_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_NEGEDGE
    };
    gpio_config(&io_conf);
    
    gpio_set_direction(INVERTER_GATE_EN, GPIO_MODE_OUTPUT);
    gpio_set_level(INVERTER_GATE_EN, 1); // Активація інвертора
    
    gpio_install_isr_service(0);
    gpio_isr_handler_add(STO_CHANNEL_1_PIN, sto_isr_handler, NULL);
    gpio_isr_handler_add(STO_CHANNEL_2_PIN, sto_isr_handler, NULL);
}
