#include "adc.h"
#include <stdio.h>

/**
 * @file adc.c
 * @brief Реалізація функціоналу оцифрування аналогових сигналів керування.
 *
 * АЦП перетворює аналогову напругу з подільника (потенціометра) у цифровий
 * кодовий відлік. Фільтрація шляхом усереднення серії вибірок запобігає
 * мікромітінгу ("дрижанню" або jitter) вала сервоприводу.
 */

static adc_config_t s_adc_config = {0};
static bool s_adc_initialized = false;

/* Симуляція аналогового джерела (керуючого потенціометра) */
static uint16_t s_simulated_potentiometer_adc = 512; /* За замовчуванням 50% (нейтраль) */

void adc_init(const adc_config_t *config)
{
    if (config == NULL) {
        return;
    }

    s_adc_config = *config;
    s_adc_initialized = true;

    /* Налаштування апаратних регістрів АЦП (умовні мультиплексор та преддільник тактування)
     * ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // Prescaler 128
     * ADMUX  = (config->use_internal_vref ? (1 << REFS0) : 0) | (config->channel & 0x07);
     */
}

uint16_t adc_read(uint8_t channel)
{
    if (!s_adc_initialized) {
        return 0;
    }

    (void)channel; /* У даній реалізації зчитується заданий канал */

    /* Імітація завершення аналого-цифрового перетворення та повернення коду:
     * ADCSRA |= (1 << ADSC); // Запуск перетворення
     * while (ADCSRA & (1 << ADSC)); // Очікування прапорця готовності
     * return ADC;
     */
    return s_simulated_potentiometer_adc;
}

uint16_t adc_read_filtered(uint8_t channel, uint8_t samples)
{
    if (samples == 0) {
        samples = 1;
    }
    if (samples > 64) {
        samples = 64;
    }

    uint32_t sum = 0;
    for (uint8_t i = 0; i < samples; i++) {
        sum += adc_read(channel);
    }

    return (uint16_t)(sum / samples);
}

float adc_to_millivolts(uint16_t adc_value)
{
    if (adc_value > ADC_MAX_VALUE) {
        adc_value = ADC_MAX_VALUE;
    }

    return ((float)adc_value / (float)ADC_MAX_VALUE) * (float)ADC_VREF_MV;
}
