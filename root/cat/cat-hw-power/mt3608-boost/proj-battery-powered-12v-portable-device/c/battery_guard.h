#ifndef BATTERY_GUARD_H
#define BATTERY_GUARD_H

#include <stdint.h>
#include <stdbool.h>

#define BATTERY_FILTER_SAMPLES 8

/**
 * @brief Статус заряду літієвого акумулятора
 */
typedef enum {
    BATTERY_OK = 0,             /* Напруга в нормі, підвищувач MT3608 працює */
    BATTERY_LOW_WARNING,        /* Напруга наближається до розряду (3.2–3.4 В) */
    BATTERY_CRITICAL_CUTOFF     /* Напруга < 3.0 В: перетворювач примусово вимкнено */
} battery_status_t;

/**
 * @brief Структура конфігурації монітора батареї
 */
typedef struct {
    uint32_t r_top_ohms;        /* Опір верхнього плеча дільника (Ом) */
    uint32_t r_bottom_ohms;     /* Опір нижнього плеча дільника (Ом) */
    uint16_t vref_mv;           /* Опорна напруга АЦП (мВ), наприклад 1100 або 3300 */
    uint16_t adc_max_ticks;     /* Максимальне значення АЦП (1023 для 10-біт, 4095 для 12-біт) */

    uint16_t cutoff_voltage_mv;   /* Поріг аварійного відключення (наприклад 3000 мВ) */
    uint16_t recovery_voltage_mv; /* Поріг відновлення з гістерезисом (наприклад 3300 мВ) */

    /* Буфер ковзного середнього для фільтрації шумів комутації 1.2 МГц */
    uint16_t history[BATTERY_FILTER_SAMPLES];
    uint8_t sample_count;
    uint8_t sample_idx;
    uint16_t filtered_voltage_mv;

    bool boost_enabled;
    battery_status_t status;
} battery_guard_t;

/**
 * @brief Ініціалізація структури захисту батареї
 */
void battery_guard_init(battery_guard_t *bg, 
                        uint32_t r_top, uint32_t r_bottom, 
                        uint16_t vref_mv, uint16_t adc_max_ticks,
                        uint16_t cutoff_mv, uint16_t recovery_mv);

/**
 * @brief Перетворення сирого коду АЦП у мілівольти на вході мікроконтролера
 */
uint16_t battery_guard_raw_to_battery_mv(const battery_guard_t *bg, uint16_t raw_adc);

/**
 * @brief Оновлення вимірів, цифрова фільтрація та керування виводом EN MT3608
 */
void battery_guard_update(battery_guard_t *bg, uint16_t raw_adc);

/**
 * @brief Перевірка, чи дозволена робота перетворювача MT3608
 */
bool battery_guard_is_boost_enabled(const battery_guard_t *bg);

/**
 * @brief Отримання поточної відфільтрованої напруги (мВ)
 */
uint16_t battery_guard_get_voltage(const battery_guard_t *bg);

#endif /* BATTERY_GUARD_H */
