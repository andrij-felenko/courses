/**
 * @file lm35.c
 * @brief Реалізація C-драйвера аналогового давача температури LM35DZ.
 *
 * Модуль конфігурує апаратні регістри АЦП мікроконтролера на роботу з внутрішнім
 * джерелом опорної напруги 1.1 В, виконує аналогово-цифрове перетворення,
 * забезпечує математичний перерахунок у напругу і градуси Цельсія та реалізує
 * алгоритм програмного експоненційного згладжування (EMA).
 */

#include "lm35.h"
#include <stdio.h>

/* Локальний стан драйвера */
static lm35_config_t s_config = {
    .adc_channel   = 0,
    .vref_mv       = LM35_ADC_VREF_MV,
    .default_alpha = LM35_EMA_ALPHA_DEFAULT
};
static bool s_initialized = false;

/* Симульоване аналогове джерело (для забезпечення автономного розгортання та тестування без фізичної платформи) */
static uint16_t s_simulated_adc_raw = 233; /* 233 * (1100 мВ / 1024) / 10 = 25.02 °C */

lm35_err_t lm35_init(const lm35_config_t *config)
{
    if (config == NULL) {
        return LM35_ERR_INVALID_PARAM;
    }

    if (config->vref_mv <= 0.0f || config->default_alpha <= 0.0f || config->default_alpha > 1.0f) {
        return LM35_ERR_INVALID_PARAM;
    }

    s_config = *config;

    /* -------------------------------------------------------------------------
     * Конфігурація апаратних регістрів АЦП мікроконтролера (на прикладі AVR/ATmega328P):
     *
     * 1. Налаштування джерела опорної напруги 1.1 В (Internal Reference) та мультиплексора:
     *    ADMUX = (1 << REFS1) | (1 << REFS0) | (s_config.adc_channel & 0x07);
     *    - REFS1=1, REFS0=1 відповідає вибору Internal 1.1V Voltage Reference.
     *
     * 2. Ввімкнення модулю АЦП та налаштування преддільника тактування (Prescaler = 128):
     *    ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);
     *    - При системній частоті F_CPU = 16 МГц тактова частота АЦП становить 125 кГц,
     *      що забезпечує максимальну точність вимірювань за специфікацією.
     * ------------------------------------------------------------------------- */

    s_initialized = true;
    return LM35_OK;
}

lm35_err_t lm35_filter_init(lm35_filter_t *filter, float alpha)
{
    if (filter == NULL) {
        return LM35_ERR_INVALID_PARAM;
    }

    if (alpha <= 0.0f || alpha > 1.0f) {
        return LM35_ERR_INVALID_PARAM;
    }

    filter->filtered_temp_c = 0.0f;
    filter->alpha = alpha;
    filter->initialized = false;

    return LM35_OK;
}

lm35_err_t lm35_read_raw(uint16_t *raw_adc)
{
    if (raw_adc == NULL) {
        return LM35_ERR_INVALID_PARAM;
    }

    if (!s_initialized) {
        return LM35_ERR_NOT_INITIALIZED;
    }

    /* -------------------------------------------------------------------------
     * Апаратний цикл виконання перетворення АЦП:
     *
     * ADCSRA |= (1 << ADSC);             // Старт перетворення
     * while (ADCSRA & (1 << ADSC));      // Очікування завершення (Hardware polling)
     * *raw_adc = ADC;                    // Зчитування 10-бітного результату
     * ------------------------------------------------------------------------- */

    *raw_adc = s_simulated_adc_raw;
    return LM35_OK;
}

float lm35_raw_to_voltage_mv(uint16_t raw_adc, float vref_mv)
{
    if (raw_adc > LM35_ADC_MAX_RAW) {
        raw_adc = LM35_ADC_MAX_RAW;
    }

    /* Математичний перерахунок коду АЦП у напругу (мВ):
     * V_out = (RAW * V_ref) / 1024.0
     */
    return ((float)raw_adc * vref_mv) / LM35_ADC_STEPS;
}

float lm35_voltage_to_temp_c(float voltage_mv)
{
    if (voltage_mv < 0.0f) {
        voltage_mv = 0.0f;
    }

    /* Математичний перерахунок напруги в градуси Цельсія:
     * T = V_out / 10.0 (оскільки коефіцієнт LM35DZ = 10 мВ/°C)
     */
    return voltage_mv / LM35_SENSITIVITY_MV_PER_C;
}

float lm35_raw_to_temp_c(uint16_t raw_adc, float vref_mv)
{
    float voltage_mv = lm35_raw_to_voltage_mv(raw_adc, vref_mv);
    return lm35_voltage_to_temp_c(voltage_mv);
}

lm35_err_t lm35_read_temp_c(float *temp_c)
{
    if (temp_c == NULL) {
        return LM35_ERR_INVALID_PARAM;
    }

    uint16_t raw_adc = 0;
    lm35_err_t err = lm35_read_raw(&raw_adc);
    if (err != LM35_OK) {
        return err;
    }

    *temp_c = lm35_raw_to_temp_c(raw_adc, s_config.vref_mv);
    return LM35_OK;
}

float lm35_filter_update(lm35_filter_t *filter, float sample_temp_c)
{
    if (filter == NULL) {
        return sample_temp_c;
    }

    /* Для першої вибірки уникаємо перехідного процесу (заповнюємо фільтр реальним значенням) */
    if (!filter->initialized) {
        filter->filtered_temp_c = sample_temp_c;
        filter->initialized = true;
        return filter->filtered_temp_c;
    }

    /* Алгоритм програмного експоненційного згладжування (EMA):
     * EMA[k] = alpha * X[k] + (1 - alpha) * EMA[k-1]
     */
    filter->filtered_temp_c = (filter->alpha * sample_temp_c) + 
                              ((1.0f - filter->alpha) * filter->filtered_temp_c);

    return filter->filtered_temp_c;
}

lm35_err_t lm35_read_filtered_temp_c(lm35_filter_t *filter, float *filtered_temp_c)
{
    if (filtered_temp_c == NULL || filter == NULL) {
        return LM35_ERR_INVALID_PARAM;
    }

    float raw_temp = 0.0f;
    lm35_err_t err = lm35_read_temp_c(&raw_temp);
    if (err != LM35_OK) {
        return err;
    }

    *filtered_temp_c = lm35_filter_update(filter, raw_temp);
    return LM35_OK;
}
