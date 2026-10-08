/**
 * @file adc_hal.c
 * @brief Реалізація низькорівневої абстракції АЦП для зчитування кондиційованого сигналу LVDT.
 */

#include "adc_hal.h"
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* Внутрішній стан налаштованої периферії АЦП */
static adc_config_t g_adc_config = {
    .channel = ADC_CHANNEL_0,
    .resolution = ADC_RES_12BIT,
    .sample_time = ADC_SAMPLETIME_239_5_CYCLES,
    .vref_volts = 3.3f
};

static bool g_adc_initialized = false;

/* Емульоване значення напруги на фізичному виході кондиціонера LVDT (в Вольтах) */
static float g_simulated_input_voltage = 1.65f;

adc_status_t adc_hal_init(const adc_config_t *config)
{
    if (config == NULL) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (config->vref_volts <= 0.0f || config->vref_volts > 10.0f) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (config->channel >= ADC_CHANNEL_MAX) {
        return ADC_ERROR_INVALID_PARAM;
    }

    /* Збереження конфігурації апаратного модуля */
    g_adc_config = *config;
    g_adc_initialized = true;

    return ADC_OK;
}

uint32_t adc_hal_get_max_code(adc_resolution_t resolution)
{
    if (resolution < ADC_RES_8BIT || resolution > ADC_RES_16BIT) {
        resolution = ADC_RES_12BIT;
    }
    return (1U << (uint32_t)resolution) - 1U;
}

adc_status_t adc_hal_read_raw(adc_channel_t channel, uint16_t *raw_value)
{
    if (raw_value == NULL) {
        return ADC_ERROR_INVALID_PARAM;
    }

    if (!g_adc_initialized) {
        /* Примусова ініціалізація за замовчуванням, якщо HAL не було явно ініціалізовано */
        g_adc_initialized = true;
    }

    (void)channel;

    uint32_t max_code = adc_hal_get_max_code(g_adc_config.resolution);

    /* Нормалізація емульованої напруги відносно VREF */
    float norm_val = g_simulated_input_voltage / g_adc_config.vref_volts;
    if (norm_val < 0.0f) {
        norm_val = 0.0f;
    }
    if (norm_val > 1.0f) {
        norm_val = 1.0f;
    }

    uint32_t code = (uint32_t)(norm_val * (float)max_code + 0.5f);
    if (code > max_code) {
        code = max_code;
    }

    *raw_value = (uint16_t)code;
    return ADC_OK;
}

adc_status_t adc_hal_read_raw_multiple(adc_channel_t channel, uint16_t *buffer, uint16_t count)
{
    if (buffer == NULL || count == 0) {
        return ADC_ERROR_INVALID_PARAM;
    }

    for (uint16_t i = 0; i < count; i++) {
        adc_status_t status = adc_hal_read_raw(channel, &buffer[i]);
        if (status != ADC_OK) {
            return status;
        }
    }

    return ADC_OK;
}

float adc_hal_raw_to_voltage(uint16_t raw_value, adc_resolution_t resolution, float vref_volts)
{
    uint32_t max_code = adc_hal_get_max_code(resolution);
    if (max_code == 0) {
        return 0.0f;
    }
    return ((float)raw_value / (float)max_code) * vref_volts;
}

/**
 * @brief Допоміжна функція тестування: встановлення фізичної напруги для емуляції переміщення LVDT.
 *
 * @param voltage_v Напруга на аналоговому вході в Вольтах.
 */
void adc_hal_set_simulated_voltage(float voltage_v)
{
    g_simulated_input_voltage = voltage_v;
}
