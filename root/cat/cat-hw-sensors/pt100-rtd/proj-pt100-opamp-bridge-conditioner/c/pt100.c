#include "pt100.h"
#include <math.h>
#include <stddef.h>

bool pt100_init_config(pt100_config_t *config,
                       uint8_t adc_bits,
                       float vref_v,
                       float temp_min,
                       float temp_max)
{
    if (config == NULL) {
        return false;
    }
    if (adc_bits == 0U || adc_bits > 32U) {
        return false;
    }
    if (vref_v <= 0.0f) {
        return false;
    }
    if (temp_min >= temp_max) {
        return false;
    }

    config->adc_bits = adc_bits;
    config->vref_v = vref_v;
    config->temp_min = temp_min;
    config->temp_max = temp_max;

    /* За замовчуванням калібрувальні коефіцієнти нейтральні */
    config->calib.gain = 1.0f;
    config->calib.offset = 0.0f;

    return true;
}

bool pt100_calc_calibration(float v_meas1, float v_ref1,
                             float v_meas2, float v_ref2,
                             pt100_calib_t *calib)
{
    if (calib == NULL) {
        return false;
    }

    float delta_meas = v_meas2 - v_meas1;

    /* Запобігання діленню на нуль, якщо виміряні значення збігаються */
    if (fabsf(delta_meas) < 1e-6f) {
        return false;
    }

    float delta_ref = v_ref2 - v_ref1;

    /*
     * Коефіцієнт нахилу прямої (gain): співвідношення діапазону еталонів до вимірів.
     * Зсув (offset): компенсує системний зсув нуля аналогового тракту.
     */
    calib->gain = delta_ref / delta_meas;
    calib->offset = v_ref1 - (calib->gain * v_meas1);

    return true;
}

float pt100_adc_to_voltage(uint32_t adc_raw, const pt100_config_t *config)
{
    if (config == NULL || config->adc_bits == 0U || config->adc_bits >= 32U) {
        return 0.0f;
    }

    /* Максимальний код для N-бітного АЦП: (2^N - 1) */
    uint32_t max_adc = (1U << config->adc_bits) - 1U;
    if (adc_raw > max_adc) {
        adc_raw = max_adc;
    }

    /* Масштабування сирого коду в діапазон 0..Vref (0–5 В) */
    return ((float)adc_raw / (float)max_adc) * config->vref_v;
}

float pt100_correct_voltage(float v_raw, const pt100_calib_t *calib)
{
    if (calib == NULL) {
        return v_raw;
    }

    /* Лінійна корекція зсуву та масштабу: V_calib = (V_raw * gain) + offset */
    return (v_raw * calib->gain) + calib->offset;
}

float pt100_voltage_to_temperature(float v_corr, const pt100_config_t *config)
{
    if (config == NULL || config->vref_v <= 0.0f) {
        return 0.0f;
    }

    /*
     * Перетворення виміряної напруги у фізичну температуру.
     * Нормувальний підсилювач перетворює зміну опору PT100 (IEC 60751) у 0–5 В.
     * Лінійна пропорція: T = T_min + (V_corr / V_ref) * (T_max - T_min)
     */
    float span_temp = config->temp_max - config->temp_min;
    float normalized_v = v_corr / config->vref_v;

    return config->temp_min + (normalized_v * span_temp);
}

bool pt100_process_sample(uint32_t adc_raw, const pt100_config_t *config, float *out_temp)
{
    if (config == NULL || out_temp == NULL) {
        return false;
    }

    /* Крок 1: Обчислення сирої напруги за кодом АЦП */
    float v_raw = pt100_adc_to_voltage(adc_raw, config);

    /* Крок 2: Застосування двохточкового калібрування */
    float v_corr = pt100_correct_voltage(v_raw, &config->calib);

    /* Крок 3: Перерахунок напруги у фізичну температуру у °C */
    float temp = pt100_voltage_to_temperature(v_corr, config);

    *out_temp = temp;

    /* Перевірка виходу виміряного значення за допустимі технологічні межі (з допуском ±10 °C) */
    if (temp < (config->temp_min - 10.0f) || temp > (config->temp_max + 10.0f)) {
        return false;
    }

    return true;
}
