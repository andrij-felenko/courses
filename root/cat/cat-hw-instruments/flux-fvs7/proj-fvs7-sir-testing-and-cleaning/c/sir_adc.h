#ifndef SIR_ADC_H
#define SIR_ADC_H

#include <stdint.h>
#include <stdbool.h>

/* Порогові значення поверхневого опору ізоляції (SIR) у Мегаомах */
#define SIR_THRESHOLD_PASS_MOHM    1000.0f  /* 1 GOm — відмінна діелектрична чистота */
#define SIR_THRESHOLD_WARN_MOHM     100.0f  /* 100 MOm — допустима межа для FVS-7 */
#define SIR_THRESHOLD_FAIL_MOHM      10.0f  /* 10 MOm — небезпека струмів витоку та корозії */

/* Константи калібрування високоомного вимірювального тракту */
#define SIR_ADC_RESOLUTION_BITS        12   /* 12-бітний АЦП (0..4095) */
#define SIR_ADC_VREF_VOLTS           3.3f   /* Опорна напруга АЦП (В) */
#define SIR_TEST_VOLTAGE_VOLTS     100.0f   /* Випробувальна напруга тестової плати (В) */
#define SIR_SENSE_RESISTOR_OHM     100000.0f/* Захисний баластний резистор вимірювача (100 кОм) */
#define SIR_FILTER_WINDOW_SIZE          8   /* Розмір вікна ковзного усереднення */

/* Стан вимірювання та діагностики SIR */
typedef enum {
    SIR_STATUS_OK = 0,
    SIR_STATUS_WARNING,
    SIR_STATUS_CRITICAL_LEAKAGE,
    SIR_STATUS_HARDWARE_FAULT
} SirStatus_t;

/* Структура конфігурації та стану високоомного каналу АЦП */
typedef struct {
    uint16_t raw_samples[SIR_FILTER_WINDOW_SIZE];
    uint8_t  sample_index;
    bool     buffer_filled;
    float    measured_voltage;
    float    leakage_current_ua;
    float    sir_resistance_mohm;
    SirStatus_t status;
    bool     alarm_active;
} SirAdcChannel_t;

/* Прототипи функцій драйвера */
void sir_adc_init(SirAdcChannel_t *channel);
bool sir_adc_update_sample(SirAdcChannel_t *channel, uint16_t raw_adc_value);
float sir_adc_calculate_resistance(float voltage_v);
SirStatus_t sir_adc_evaluate_status(float resistance_mohm);

#endif /* SIR_ADC_H */
