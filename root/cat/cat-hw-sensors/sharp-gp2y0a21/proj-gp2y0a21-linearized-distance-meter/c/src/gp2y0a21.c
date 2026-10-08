/**
 * @file gp2y0a21.c
 * @brief Реалізація алгоритмів обробки сигналу аналогового ІЧ-далекоміра Sharp GP2Y0A21YK0F.
 *
 * Виконує серійний збір даних, медіанну фільтрацію для усунення аналогових викидів,
 * перетворення сигналу у сантиметри за допомогою формули лінеаризації d = A / (ADC - B)
 * та контроль межових значень 10-80 см.
 */

#include "gp2y0a21.h"

/**
 * @brief Допоміжна функція сортування масиву для медіанної фільтрації (сортування вставками).
 */
static void insertion_sort(uint16_t *arr, uint8_t n)
{
    for (uint8_t i = 1; i < n; i++) {
        uint16_t key = arr[i];
        int j = (int)i - 1;

        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

gp2y0a21_status_t gp2y0a21_init(gp2y0a21_t *dev, const gp2y0a21_config_t *config, adc_resolution_t resolution, float vref_volts)
{
    if (dev == NULL || config == NULL) {
        return GP2Y0A21_ERROR_NULL_POINTER;
    }

    if (config->sample_count == 0 || config->sample_count > GP2Y0A21_MAX_SAMPLE_COUNT) {
        return GP2Y0A21_ERROR_INVALID_PARAM;
    }

    if (config->min_distance_cm >= config->max_distance_cm || config->coeff_a <= 0.0f) {
        return GP2Y0A21_ERROR_INVALID_PARAM;
    }

    dev->config = *config;
    dev->resolution = resolution;
    dev->vref_volts = vref_volts;
    dev->is_initialized = true;

    return GP2Y0A21_OK;
}

gp2y0a21_status_t gp2y0a21_read_samples(gp2y0a21_t *dev, uint16_t *samples_out, uint8_t count)
{
    if (dev == NULL || samples_out == NULL) {
        return GP2Y0A21_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return GP2Y0A21_ERROR_INVALID_PARAM;
    }

    if (count == 0 || count > GP2Y0A21_MAX_SAMPLE_COUNT) {
        return GP2Y0A21_ERROR_INVALID_PARAM;
    }

    for (uint8_t i = 0; i < count; i++) {
        adc_status_t status = adc_hal_read_raw_blocking(dev->config.adc_channel, &samples_out[i]);
        if (status != ADC_OK) {
            return GP2Y0A21_ERROR_ADC_READ;
        }
    }

    return GP2Y0A21_OK;
}

uint16_t gp2y0a21_filter_median(uint16_t *samples, uint8_t count)
{
    if (samples == NULL || count == 0) {
        return 0;
    }

    if (count == 1) {
        return samples[0];
    }

    /* Копіюємо вибірки у локальний масив для безпечного сортування */
    uint16_t temp_buffer[GP2Y0A21_MAX_SAMPLE_COUNT];
    uint8_t actual_count = (count > GP2Y0A21_MAX_SAMPLE_COUNT) ? GP2Y0A21_MAX_SAMPLE_COUNT : count;

    for (uint8_t i = 0; i < actual_count; i++) {
        temp_buffer[i] = samples[i];
    }

    insertion_sort(temp_buffer, actual_count);

    /* Якщо кількість вибірок парна — беремо середнє арифметичне двох центральних */
    if (actual_count % 2 == 0) {
        return (uint16_t)(((uint32_t)temp_buffer[actual_count / 2 - 1] + temp_buffer[actual_count / 2]) / 2U);
    }

    return temp_buffer[actual_count / 2];
}

gp2y0a21_status_t gp2y0a21_convert_to_distance(const gp2y0a21_t *dev, uint16_t adc_raw, float *distance_out)
{
    if (dev == NULL || distance_out == NULL) {
        return GP2Y0A21_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return GP2Y0A21_ERROR_INVALID_PARAM;
    }

    /*
     * Формула лінеаризації: d = A / (ADC_raw - B)
     * Якщо ADC_raw <= B, знаменник від'ємний або нульовий, що відповідає віддаленому об'єкту
     * за межами вимірюваного діапазону.
     */
    float denominator = (float)adc_raw - dev->config.coeff_b;
    if (denominator <= 1.0f) {
        *distance_out = dev->config.max_distance_cm + 1.0f;
        return GP2Y0A21_OUT_OF_BOUNDS_TOO_FAR;
    }

    float calc_dist = dev->config.coeff_a / denominator;
    *distance_out = calc_dist;

    return gp2y0a21_validate_bounds(dev, calc_dist);
}

gp2y0a21_status_t gp2y0a21_validate_bounds(const gp2y0a21_t *dev, float distance_cm)
{
    if (dev == NULL) {
        return GP2Y0A21_ERROR_NULL_POINTER;
    }

    if (distance_cm < dev->config.min_distance_cm) {
        return GP2Y0A21_OUT_OF_BOUNDS_TOO_CLOSE;
    }

    if (distance_cm > dev->config.max_distance_cm) {
        return GP2Y0A21_OUT_OF_BOUNDS_TOO_FAR;
    }

    return GP2Y0A21_OK;
}

gp2y0a21_status_t gp2y0a21_read_distance(gp2y0a21_t *dev, gp2y0a21_reading_t *reading)
{
    if (dev == NULL || reading == NULL) {
        return GP2Y0A21_ERROR_NULL_POINTER;
    }

    if (!dev->is_initialized) {
        return GP2Y0A21_ERROR_INVALID_PARAM;
    }

    uint16_t samples[GP2Y0A21_MAX_SAMPLE_COUNT];
    uint8_t count = dev->config.sample_count;

    /* Крок 1: Збір масиву вибірок з АЦП */
    gp2y0a21_status_t status = gp2y0a21_read_samples(dev, samples, count);
    if (status != GP2Y0A21_OK) {
        reading->status = status;
        return status;
    }

    /* Крок 2: Програмна медіанна фільтрація для відсікання сплесків */
    reading->raw_adc_median = gp2y0a21_filter_median(samples, count);

    /* Крок 3: Перетворення цифрового значення в аналогову напругу у вольтах */
    reading->voltage_v = adc_hal_raw_to_voltage(reading->raw_adc_median, dev->resolution, dev->vref_volts);

    /* Крок 4: Лінеаризація нелінійного сигналу та валідація діапазону 10-80 см */
    status = gp2y0a21_convert_to_distance(dev, reading->raw_adc_median, &reading->distance_cm);
    reading->status = status;

    return status;
}
