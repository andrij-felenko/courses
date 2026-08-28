#include <stdint.h>
#include <stdbool.h>

/* Конфігурація резистивного дільника та АЦП */
typedef struct {
    uint32_t r1_ohms;            /* Опір верхнього плеча (наприклад, 100000) */
    uint32_t r2_ohms;            /* Опір нижнього плеча (наприклад, 200000) */
    uint16_t vref_mv;            /* Опорна напруга АЦП у мВ (наприклад, 3300) */
    uint16_t adc_max_code;       /* Максимальний код АЦП (4095 для 12 біт) */
    int16_t  cal_offset_mv;      /* Зсув нуля з EEPROM (калібрування) */
    uint16_t cal_gain_ppm;       /* Масштабний коефіцієнт (1000000 = 1.0000) */
} adc_divider_channel_t;

/**
 * @brief Перетворення сирого коду АЦП у реальну напругу акумулятора в мілівольтах
 * Розрахунок ведеться у 64-бітних цілих числах для уникнення переповнення та втрати точності
 */
uint32_t adc_to_battery_voltage_mv(uint16_t raw_code, const adc_divider_channel_t *ch) {
    if (ch == NULL || ch->adc_max_code == 0 || ch->r2_ohms == 0) {
        return 0;
    }

    /* 1. Напруга на вході піна АЦП: V_pin = (raw_code * Vref) / ADC_MAX */
    uint64_t v_pin_mv = ((uint64_t)raw_code * (uint64_t)ch->vref_mv) / (uint64_t)ch->adc_max_code;

    /* 2. Масштабування через коефіцієнт дільника: Vin = V_pin * (R1 + R2) / R2 */
    uint64_t r_sum = (uint64_t)ch->r1_ohms + (uint64_t)ch->r2_ohms;
    uint64_t v_bat_raw = (v_pin_mv * r_sum) / (uint64_t)ch->r2_ohms;

    /* 3. Застосування заводського калібрування (зсув та нахил) */
    int64_t v_calibrated = (int64_t)v_bat_raw + (int64_t)ch->cal_offset_mv;
    if (ch->cal_gain_ppm != 0 && ch->cal_gain_ppm != 1000000) {
        v_calibrated = (v_calibrated * (int64_t)ch->cal_gain_ppm) / 1000000;
    }

    return (v_calibrated > 0) ? (uint32_t)v_calibrated : 0;
}
