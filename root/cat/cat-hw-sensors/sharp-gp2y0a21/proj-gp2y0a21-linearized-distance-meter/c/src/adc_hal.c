/**
 * @file adc_hal.c
 * @brief Реалізація апаратного рівня абстракції (HAL) для АЦП мікроконтролера.
 *
 * Модуль забезпечує ініціалізацію аналогово-цифрової периферії, вибір часу
 * накопичення заряду та виконання вимірювань для підключених сенсорів.
 */

#include "adc_hal.h"

/**
 * @brief Внутрішній стан каналу АЦП
 */
typedef struct {
    adc_config_t config;
    bool is_initialized;
    bool is_converting;
    uint16_t simulated_raw;
} adc_channel_state_t;

/** Масив станів каналів АЦП */
static adc_channel_state_t s_channels[ADC_HAL_MAX_CHANNELS];

adc_status_t adc_hal_init(adc_channel_t channel, const adc_config_t *config)
{
    if (channel >= ADC_HAL_MAX_CHANNELS || config == NULL) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (config->vref_volts <= 0.0f) {
        return ADC_ERROR_INVALID_PARAM;
    }

    s_channels[channel].config = *config;
    s_channels[channel].is_initialized = true;
    s_channels[channel].is_converting = false;
    s_channels[channel].simulated_raw = 0;

    return ADC_OK;
}

uint16_t adc_hal_get_max_value(adc_resolution_t resolution)
{
    if (resolution == ADC_RES_10BIT) {
        return 1023U;
    }
    return 4095U;
}

adc_status_t adc_hal_read_raw_blocking(adc_channel_t channel, uint16_t *raw_value)
{
    if (channel >= ADC_HAL_MAX_CHANNELS || raw_value == NULL) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (!s_channels[channel].is_initialized) {
        return ADC_ERROR_NOT_INITIALIZED;
    }

    /*
     * Симуляція читання з апаратного регістра АЦП мікроконтролера.
     * У реальній прошивці тут відбувається запуск перетворення, очікування
     * прапорця завершення (EOC) та зчитування регістра ADC->DR.
     */
    uint16_t max_val = adc_hal_get_max_value(s_channels[channel].config.resolution);
    
    /* Якщо під час симуляції значення не задано зовні, повертаємо середній рівень */
    if (s_channels[channel].simulated_raw == 0) {
        *raw_value = (uint16_t)(max_val * 0.35f);
    } else {
        *raw_value = s_channels[channel].simulated_raw;
    }

    return ADC_OK;
}

adc_status_t adc_hal_start_non_blocking(adc_channel_t channel)
{
    if (channel >= ADC_HAL_MAX_CHANNELS) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (!s_channels[channel].is_initialized) {
        return ADC_ERROR_NOT_INITIALIZED;
    }

    if (s_channels[channel].is_converting) {
        return ADC_ERROR_BUSY;
    }

    s_channels[channel].is_converting = true;
    return ADC_OK;
}

adc_status_t adc_hal_get_non_blocking_result(adc_channel_t channel, uint16_t *raw_value, bool *is_ready)
{
    if (channel >= ADC_HAL_MAX_CHANNELS || raw_value == NULL || is_ready == NULL) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (!s_channels[channel].is_initialized) {
        *is_ready = false;
        return ADC_ERROR_NOT_INITIALIZED;
    }

    if (!s_channels[channel].is_converting) {
        *is_ready = false;
        return ADC_OK;
    }

    /* Симуляція завершення асинхронного перетворення АЦП */
    s_channels[channel].is_converting = false;
    *is_ready = true;
    
    return adc_hal_read_raw_blocking(channel, raw_value);
}

float adc_hal_raw_to_voltage(uint16_t raw_value, adc_resolution_t resolution, float vref_volts)
{
    uint16_t max_adc = adc_hal_get_max_value(resolution);
    if (raw_value > max_adc) {
        raw_value = max_adc;
    }
    return ((float)raw_value / (float)max_adc) * vref_volts;
}
