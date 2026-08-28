#include <stdint.h>
#include <stdbool.h>

#define ADC_MAX_CODE       4095
#define FILTER_SHIFT       4      /* alpha = 1/16 */
#define LUT_ENTRIES        33
#define LUT_STEP_SHIFT     7      /* крок 128 відліків */
#define LUT_STEP_MASK      0x7F

typedef struct {
    uint32_t filter_acc;  /* Накопичувач БІХ-фільтра (формат Q12.4) */
    bool is_initialized;  /* Прапорець першого запуску */
} SensorChannel;

/* Таблиця калібрувальних температур у сотих частках °C (наприклад, 2500 = 25.00 °C) */
static const int16_t ntc_lut_centicelsius[LUT_ENTRIES] = {
    -4000, -3200, -2500, -1900, -1400,  -960,  -560,  -200,
      130,   440,   740,  1030,  1320,  1610,  1900,  2200,
     2500,  2810,  3130,  3470,  3830,  4220,  4650,  5130,
     5680,  6320,  7090,  8040,  9260, 10900, 13200, 16500,
    20000
};

void sensor_channel_init(SensorChannel *ch)
{
    ch->filter_acc = 0;
    ch->is_initialized = false;
}

/**
 * @brief Повний конвеєр обробки відліку: фільтрація + інтерполяція.
 * @param ch Структура стану каналу.
 * @param raw_adc Сирий відлік від АЦП [0..4095].
 * @param out_temp_c Вказівник на вихідну температуру в сотих частках °C.
 * @return true при успішному обчисленні.
 */
bool sensor_process_sample(SensorChannel *ch, uint16_t raw_adc, int16_t *out_temp_c)
{
    if (ch == NULL || out_temp_c == NULL) {
        return false;
    }

    if (raw_adc > ADC_MAX_CODE) {
        raw_adc = ADC_MAX_CODE;
    }

    /* 1. Цифрова експоненційна фільтрація */
    if (!ch->is_initialized) {
        ch->filter_acc = (uint32_t)raw_adc << FILTER_SHIFT;
        ch->is_initialized = true;
    } else {
        ch->filter_acc = ch->filter_acc + raw_adc - (ch->filter_acc >> FILTER_SHIFT);
    }

    uint16_t filtered_code = (uint16_t)(ch->filter_acc >> FILTER_SHIFT);

    /* 2. Швидка таблична інтерполяція */
    uint32_t idx = filtered_code >> LUT_STEP_SHIFT;
    uint32_t rem = filtered_code & LUT_STEP_MASK;

    if (idx >= (LUT_ENTRIES - 1)) {
        *out_temp_c = ntc_lut_centicelsius[LUT_ENTRIES - 1];
        return true;
    }

    int32_t t0 = ntc_lut_centicelsius[idx];
    int32_t t1 = ntc_lut_centicelsius[idx + 1];

    /* Лінійна апроксимація: T = T0 + (T1 - T0) * rem / 128 */
    int32_t delta = t1 - t0;
    int32_t interpolated = t0 + ((delta * (int32_t)rem) >> LUT_STEP_SHIFT);

    *out_temp_c = (int16_t)interpolated;
    return true;
}
