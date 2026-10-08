/**
 * @file lvdt.c
 * @brief Реалізація драйвера та математичних алгоритмів обробки сигналу LVDT.
 */

#include "lvdt.h"
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

lvdt_status_t lvdt_init(lvdt_t *dev, const lvdt_config_t *config)
{
    if (dev == NULL || config == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    if (config->vref_volts <= 0.0f || config->sensitivity_mm_per_v == 0.0f) {
        return LVDT_ERROR_INVALID_PARAM;
    }

    if (config->filter_alpha <= 0.0f || config->filter_alpha > 1.0f) {
        return LVDT_ERROR_INVALID_PARAM;
    }

    if (config->min_displacement_mm >= config->max_displacement_mm) {
        return LVDT_ERROR_INVALID_PARAM;
    }

    if (config->min_valid_voltage_v >= config->max_valid_voltage_v) {
        return LVDT_ERROR_INVALID_PARAM;
    }

    dev->config = *config;
    
    /* За замовчуванням нуль встановлюється посередині шкали VREF */
    dev->zero_offset_volts = config->vref_volts / 2.0f;
    dev->filtered_voltage_v = dev->zero_offset_volts;
    dev->is_zero_calibrated = false;

    /* Ініціалізація апаратного рівня абстракції АЦП */
    adc_config_t adc_cfg = {
        .channel = config->adc_channel,
        .resolution = config->adc_resolution,
        .sample_time = config->sample_time,
        .vref_volts = config->vref_volts
    };

    if (adc_hal_init(&adc_cfg) != ADC_OK) {
        return LVDT_ERROR_ADC;
    }

    dev->is_initialized = true;
    return LVDT_OK;
}

lvdt_status_t lvdt_calibrate_zero(lvdt_t *dev, uint16_t num_samples)
{
    if (dev == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return LVDT_ERROR_NOT_INITIALIZED;
    }

    if (num_samples == 0) {
        num_samples = LVDT_DEFAULT_CALIB_SAMPLES;
    }

    double voltage_sum = 0.0;

    for (uint16_t i = 0; i < num_samples; i++) {
        uint16_t raw_code = 0;
        adc_status_t status = adc_hal_read_raw(dev->config.adc_channel, &raw_code);
        if (status != ADC_OK) {
            return LVDT_ERROR_ADC;
        }

        float v = adc_hal_raw_to_voltage(raw_code, dev->config.adc_resolution, dev->config.vref_volts);
        voltage_sum += v;
    }

    float avg_zero = (float)(voltage_sum / (double)num_samples);

    /* Перевірка чи потрапляє виміряний нуль у допустимий аналоговий діапазон */
    if (avg_zero < dev->config.min_valid_voltage_v || avg_zero > dev->config.max_valid_voltage_v) {
        return LVDT_ERROR_SIGNAL_FAULT;
    }

    dev->zero_offset_volts = avg_zero;
    dev->filtered_voltage_v = avg_zero;
    dev->is_zero_calibrated = true;

    return LVDT_OK;
}

lvdt_status_t lvdt_set_zero_offset(lvdt_t *dev, float zero_volts)
{
    if (dev == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return LVDT_ERROR_NOT_INITIALIZED;
    }

    if (zero_volts < dev->config.min_valid_voltage_v || zero_volts > dev->config.max_valid_voltage_v) {
        return LVDT_ERROR_INVALID_PARAM;
    }

    dev->zero_offset_volts = zero_volts;
    dev->filtered_voltage_v = zero_volts;
    dev->is_zero_calibrated = true;

    return LVDT_OK;
}

lvdt_status_t lvdt_read_raw_voltage(lvdt_t *dev, float *voltage_out)
{
    if (dev == NULL || voltage_out == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return LVDT_ERROR_NOT_INITIALIZED;
    }

    uint16_t raw_code = 0;
    if (adc_hal_read_raw(dev->config.adc_channel, &raw_code) != ADC_OK) {
        return LVDT_ERROR_ADC;
    }

    *voltage_out = adc_hal_raw_to_voltage(raw_code, dev->config.adc_resolution, dev->config.vref_volts);
    return LVDT_OK;
}

float lvdt_apply_ema_filter(lvdt_t *dev, float new_voltage)
{
    if (dev == NULL) {
        return new_voltage;
    }

    float alpha = dev->config.filter_alpha;
    /* Формула EMA: y[n] = alpha * x[n] + (1 - alpha) * y[n-1] */
    dev->filtered_voltage_v = (alpha * new_voltage) + ((1.0f - alpha) * dev->filtered_voltage_v);

    return dev->filtered_voltage_v;
}

lvdt_status_t lvdt_convert_voltage_to_displacement(const lvdt_t *dev, float voltage_v, float *displacement_mm)
{
    if (dev == NULL || displacement_mm == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return LVDT_ERROR_NOT_INITIALIZED;
    }

    /* Delta V = V_in - V_zero */
    float delta_v = voltage_v - dev->zero_offset_volts;

    /* x = Delta V * S (мм/В) */
    *displacement_mm = delta_v * dev->config.sensitivity_mm_per_v;

    return LVDT_OK;
}

lvdt_status_t lvdt_validate_signal(const lvdt_t *dev, float voltage_v, float displacement_mm)
{
    if (dev == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    /* 1. Перевірка аналогового сигналу на обрив або КЗ */
    if (voltage_v < dev->config.min_valid_voltage_v || voltage_v > dev->config.max_valid_voltage_v) {
        return LVDT_ERROR_SIGNAL_FAULT;
    }

    /* 2. Перевірка виходу сердечника за робочі межі переміщення */
    if (displacement_mm < dev->config.min_displacement_mm) {
        return LVDT_WARN_OUT_OF_RANGE_MIN;
    }
    if (displacement_mm > dev->config.max_displacement_mm) {
        return LVDT_WARN_OUT_OF_RANGE_MAX;
    }

    return LVDT_OK;
}

lvdt_status_t lvdt_process_sample(lvdt_t *dev, lvdt_reading_t *reading)
{
    if (dev == NULL || reading == NULL) {
        return LVDT_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return LVDT_ERROR_NOT_INITIALIZED;
    }

    /* 1. Зчитування коду АЦП */
    uint16_t raw_code = 0;
    if (adc_hal_read_raw(dev->config.adc_channel, &raw_code) != ADC_OK) {
        reading->status = LVDT_ERROR_ADC;
        return LVDT_ERROR_ADC;
    }
    reading->raw_adc = raw_code;

    /* 2. Перетворення у сиру напругу */
    reading->raw_voltage_v = adc_hal_raw_to_voltage(raw_code, dev->config.adc_resolution, dev->config.vref_volts);

    /* 3. Цифрова EMA фільтрація */
    reading->filtered_voltage_v = lvdt_apply_ema_filter(dev, reading->raw_voltage_v);

    /* 4. Обчислення лінійного переміщення */
    lvdt_status_t conv_status = lvdt_convert_voltage_to_displacement(dev, reading->filtered_voltage_v, &reading->displacement_mm);
    if (conv_status != LVDT_OK) {
        reading->status = conv_status;
        return conv_status;
    }

    /* 5. Валідація та діагностика */
    reading->status = lvdt_validate_signal(dev, reading->raw_voltage_v, reading->displacement_mm);

    return reading->status;
}

void lvdt_reset_filter(lvdt_t *dev)
{
    if (dev != NULL && dev->is_initialized) {
        dev->filtered_voltage_v = dev->zero_offset_volts;
    }
}
