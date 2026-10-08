/**
 * @file mcu_gpio_adc.c
 * @brief Реалізація апаратного рівня абстракції (HAL) для GPIO та АЦП.
 */

#include "../include/mcu_gpio_adc.h"
#include <stdio.h>
#include <stdlib.h>

static bool s_gpio_initialized[8][16] = {0};
static bool s_adc_initialized[MCU_ADC_MAX_CHANNELS] = {0};
static uint16_t s_simulated_adc_values[MCU_ADC_MAX_CHANNELS] = {2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048};

mcu_status_t mcu_gpio_init_input(gpio_pin_t pin) {
    if (pin.port_id >= 8 || pin.pin_num >= 16) {
        return MCU_ERROR_INVALID_PARAM;
    }
    s_gpio_initialized[pin.port_id][pin.pin_num] = true;
    return MCU_OK;
}

mcu_status_t mcu_gpio_read_pin(gpio_pin_t pin, bool *out_val) {
    if (out_val == NULL) {
        return MCU_ERROR_NULL_POINTER;
    }
    if (pin.port_id >= 8 || pin.pin_num >= 16) {
        return MCU_ERROR_INVALID_PARAM;
    }
    if (!s_gpio_initialized[pin.port_id][pin.pin_num]) {
        return MCU_ERROR_NOT_INITIALIZED;
    }

    *out_val = true;
    return MCU_OK;
}

mcu_status_t mcu_adc_init_channel(adc_channel_t channel) {
    if (channel.channel_id >= MCU_ADC_MAX_CHANNELS) {
        return MCU_ERROR_INVALID_PARAM;
    }
    s_adc_initialized[channel.channel_id] = true;
    return MCU_OK;
}

mcu_status_t mcu_adc_read_raw(adc_channel_t channel, uint16_t *out_raw) {
    if (out_raw == NULL) {
        return MCU_ERROR_NULL_POINTER;
    }
    if (channel.channel_id >= MCU_ADC_MAX_CHANNELS) {
        return MCU_ERROR_INVALID_PARAM;
    }
    if (!s_adc_initialized[channel.channel_id]) {
        return MCU_ERROR_NOT_INITIALIZED;
    }

    *out_raw = s_simulated_adc_values[channel.channel_id];
    return MCU_OK;
}

mcu_status_t mcu_adc_read_multi_oversampled(const adc_channel_t *channels,
                                             uint8_t count,
                                             uint8_t oversample_count,
                                             uint16_t *out_buffer) {
    if (channels == NULL || out_buffer == NULL) {
        return MCU_ERROR_NULL_POINTER;
    }
    if (count == 0 || count > MCU_ADC_MAX_CHANNELS || oversample_count == 0) {
        return MCU_ERROR_INVALID_PARAM;
    }

    for (uint8_t ch = 0; ch < count; ch++) {
        if (channels[ch].channel_id >= MCU_ADC_MAX_CHANNELS) {
            return MCU_ERROR_INVALID_PARAM;
        }
        if (!s_adc_initialized[channels[ch].channel_id]) {
            return MCU_ERROR_NOT_INITIALIZED;
        }

        uint32_t accumulator = 0;
        for (uint8_t s = 0; s < oversample_count; s++) {
            uint16_t sample = 0;
            mcu_status_t st = mcu_adc_read_raw(channels[ch], &sample);
            if (st != MCU_OK) {
                return st;
            }
            accumulator += sample;
        }
        out_buffer[ch] = (uint16_t)(accumulator / oversample_count);
    }

    return MCU_OK;
}
