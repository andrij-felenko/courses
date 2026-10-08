#include "adc_current_sensor.h"
#include <math.h>
#include <string.h>

int adc_sensor_init(adc_sensor_t *sensor, float shunt_resistor_ohms, float gain, float ref_voltage_v)
{
    if (sensor == NULL) {
        return -1;
    }
    if (shunt_resistor_ohms <= 0.0f || gain <= 0.0f || ref_voltage_v <= 0.0f) {
        return -1;
    }

    sensor->shunt_resistor_ohms = shunt_resistor_ohms;
    sensor->amplifier_gain = gain;
    sensor->reference_voltage_v = ref_voltage_v;

    adc_sensor_reset_buffer(sensor);
    return 0;
}

void adc_sensor_reset_buffer(adc_sensor_t *sensor)
{
    if (sensor == NULL) {
        return;
    }

    memset(sensor->raw_samples, 0, sizeof(sensor->raw_samples));
    sensor->head_index = 0U;
    sensor->sample_count = 0U;
    sensor->raw_sum = 0U;
    sensor->last_instant_ma = 0.0f;
    sensor->last_rms_ma = 0.0f;
    sensor->last_update_ms = 0U;
}

void adc_sensor_push_sample(adc_sensor_t *sensor, uint16_t raw_adc, uint32_t timestamp_ms)
{
    if (sensor == NULL) {
        return;
    }

    /* Віднімаємо стару вибірку з суми, якщо буфер заповнений */
    if (sensor->sample_count >= ADC_SENSOR_BUFFER_SIZE) {
        sensor->raw_sum -= sensor->raw_samples[sensor->head_index];
    } else {
        sensor->sample_count++;
    }

    /* Записуємо нове значення */
    sensor->raw_samples[sensor->head_index] = raw_adc;
    sensor->raw_sum += raw_adc;

    /* Переміщуємо вказівник кільцевого буфера */
    sensor->head_index = (sensor->head_index + 1U) % ADC_SENSOR_BUFFER_SIZE;
    sensor->last_update_ms = timestamp_ms;

    /* Розрахунок миттєвого струму: I = (V_adc / Gain) / R_shunt * 1000 (в мА) */
    float voltage_v = ((float)raw_adc / ADC_SENSOR_MAX_RAW) * sensor->reference_voltage_v;
    float shunt_voltage_v = voltage_v / sensor->amplifier_gain;
    sensor->last_instant_ma = (shunt_voltage_v / sensor->shunt_resistor_ohms) * 1000.0f;
}

float adc_sensor_calculate_rms(adc_sensor_t *sensor)
{
    if (sensor == NULL || sensor->sample_count == 0U) {
        return 0.0f;
    }

    /* Обчислення масштабуючого коефіцієнта перетворення сирого ADC у міліампери */
    float lsb_voltage_v = sensor->reference_voltage_v / ADC_SENSOR_MAX_RAW;
    float scale_factor = (lsb_voltage_v / (sensor->amplifier_gain * sensor->shunt_resistor_ohms)) * 1000.0f;

    float sum_squares = 0.0f;
    for (size_t i = 0U; i < sensor->sample_count; ++i) {
        float current_ma = (float)sensor->raw_samples[i] * scale_factor;
        sum_squares += current_ma * current_ma;
    }

    float mean_square = sum_squares / (float)sensor->sample_count;
    sensor->last_rms_ma = sqrtf(mean_square);

    return sensor->last_rms_ma;
}

float adc_sensor_get_instant_ma(const adc_sensor_t *sensor)
{
    if (sensor == NULL) {
        return 0.0f;
    }
    return sensor->last_instant_ma;
}
