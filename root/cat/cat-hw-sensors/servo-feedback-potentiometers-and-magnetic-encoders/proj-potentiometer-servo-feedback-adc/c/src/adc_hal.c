#include "adc_hal.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

bool adc_hal_init(adc_handle_t *handle, uint8_t channel_id, adc_resolution_t res, float vref_volts) {
    if (handle == NULL || vref_volts <= 0.0f) {
        return false;
    }

    handle->config.channel_id = channel_id;
    handle->config.resolution = res;
    handle->config.vref_volts = vref_volts;
    handle->config.sampling_time_cycles = 15; // Стандартний час вибірки для стабілізації напруги
    
    handle->is_initialized = true;
    handle->simulated_input_volts = 0.0f;
    handle->noise_amplitude_volts = 0.0f;

    return true;
}

void adc_hal_set_simulated_input(adc_handle_t *handle, float target_volts, float noise_volts) {
    if (handle == NULL) {
        return;
    }

    if (target_volts < 0.0f) {
        target_volts = 0.0f;
    } else if (target_volts > handle->config.vref_volts) {
        target_volts = handle->config.vref_volts;
    }

    handle->simulated_input_volts = target_volts;
    handle->noise_amplitude_volts = noise_volts;
}

uint16_t adc_hal_read_raw(adc_handle_t *handle) {
    if (handle == NULL || !handle->is_initialized) {
        return 0;
    }

    // Симуляція фізичного аналогового сигналу зі зворотного зв'язку потенціометра/магнітного енкодера.
    // Електрична лінія піддається впливу теплового шуму та завад драйвера мотора.
    float noise = 0.0f;
    if (handle->noise_amplitude_volts > 0.0f) {
        float r = (float)rand() / (float)RAND_MAX; // [0.0, 1.0]
        noise = (r * 2.0f - 1.0f) * handle->noise_amplitude_volts;
    }

    float measured_volts = handle->simulated_input_volts + noise;

    // Насичення в межах фізичних рейок живлення АЦП [0, Vref]
    if (measured_volts < 0.0f) {
        measured_volts = 0.0f;
    } else if (measured_volts > handle->config.vref_volts) {
        measured_volts = handle->config.vref_volts;
    }

    // Аналогово-цифрове перетворення (квантування): N = floor((V_in / V_ref) * N_max + 0.5)
    float normalized = measured_volts / handle->config.vref_volts;
    uint32_t raw_code = (uint32_t)(normalized * (float)handle->config.resolution + 0.5f);

    if (raw_code > (uint32_t)handle->config.resolution) {
        raw_code = (uint32_t)handle->config.resolution;
    }

    return (uint16_t)raw_code;
}

float adc_hal_raw_to_volts(const adc_handle_t *handle, uint16_t raw_val) {
    if (handle == NULL || handle->config.resolution == 0) {
        return 0.0f;
    }
    return ((float)raw_val / (float)handle->config.resolution) * handle->config.vref_volts;
}
