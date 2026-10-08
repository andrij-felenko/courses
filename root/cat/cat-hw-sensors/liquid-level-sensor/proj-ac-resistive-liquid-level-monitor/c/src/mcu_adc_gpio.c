#include "mcu_adc_gpio.h"
#include <string.h>

#define MAX_SIM_PINS 32
#define MAX_SIM_ADC_CHANNELS 8

static bool g_gpio_states[MAX_SIM_PINS] = {false};
static bool g_gpio_dirs[MAX_SIM_PINS] = {MCU_GPIO_DIR_INPUT};
static uint16_t g_adc_channels[MAX_SIM_ADC_CHANNELS] = {0};

bool mcu_gpio_init(uint8_t pin, uint8_t direction) {
    if (pin >= MAX_SIM_PINS) return false;
    g_gpio_dirs[pin] = direction;
    return true;
}

bool mcu_gpio_read(uint8_t pin) {
    if (pin >= MAX_SIM_PINS) return false;
    return g_gpio_states[pin];
}

bool mcu_gpio_write(uint8_t pin, bool state) {
    if (pin >= MAX_SIM_PINS) return false;
    g_gpio_states[pin] = state;
    return true;
}

bool mcu_adc_init(void) {
    return true;
}

bool mcu_adc_read_raw(uint8_t channel, uint16_t *out_val) {
    if (channel >= MAX_SIM_ADC_CHANNELS || out_val == NULL) return false;
    *out_val = g_adc_channels[channel];
    return true;
}

void mcu_sim_set_adc_raw(uint8_t channel, uint16_t raw_val) {
    if (channel < MAX_SIM_ADC_CHANNELS) {
        g_adc_channels[channel] = raw_val;
    }
}

void mcu_sim_set_gpio(uint8_t pin, bool state) {
    if (pin < MAX_SIM_PINS) {
        g_gpio_states[pin] = state;
    }
}

bool mcu_sim_get_gpio(uint8_t pin) {
    if (pin < MAX_SIM_PINS) {
        return g_gpio_states[pin];
    }
    return false;
}
