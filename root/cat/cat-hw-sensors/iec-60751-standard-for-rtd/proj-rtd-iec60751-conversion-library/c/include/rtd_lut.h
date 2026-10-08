#ifndef RTD_LUT_H
#define RTD_LUT_H

#include "rtd_iec60751.h"
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file rtd_lut.h
 * @brief Оголошення інтерфейсу табличної інтерполяції (LUT) для мікроконтролерів без FPU.
 */

#define RTD_LUT_STEP_DEG      10       /* Крок температури у таблиці (°C) */
#define RTD_LUT_MIN_TEMP     -200      /* Мінімальна температура (°C) */
#define RTD_LUT_MAX_TEMP      850      /* Максимальна температура (°C) */
#define RTD_LUT_ELEMENT_COUNT (((RTD_LUT_MAX_TEMP - RTD_LUT_MIN_TEMP) / RTD_LUT_STEP_DEG) + 1)

/**
 * @brief Таблиця пошуку (LUT) для цілочисельного перетворення опору в температуру.
 * Значення опору зберігаються у міліомах (мОм) для високої точності без плаваючої крапки.
 */
typedef struct {
    rtd_type_t type;                                 /* Тип RTD (Pt100 або Pt1000) */
    int32_t min_temp_mc;                             /* Мінімальна температура в міліградусах Цельсія (м°C) */
    int32_t step_temp_mc;                            /* Крок температури в міліградусах Цельсія (м°C) */
    size_t size;                                     /* Кількість елементів в таблиці */
    uint32_t resistance_mohm[RTD_LUT_ELEMENT_COUNT]; /* Масив опорів у міліомах */
} rtd_lut_t;

/**
 * @brief Ініціалізація та генерація таблиці LUT для заданого типу RTD.
 *
 * @param lut Вказівник на структуру LUT
 * @param type Тип термоопору (Pt100 або Pt1000)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_lut_init(rtd_lut_t *lut, rtd_type_t type);

/**
 * @brief Лінійна інтерполяція температури за опором у міліомах (цілочисельний алгоритм).
 *
 * @param lut Вказівник на таблицю LUT
 * @param resistance_mohm Виміряний опір у міліомах (мОм)
 * @param temp_mc Вихідна температура в міліградусах Цельсія (м°C)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_lut_lookup_temp_mc(const rtd_lut_t *lut, uint32_t resistance_mohm, int32_t *temp_mc);

/**
 * @brief Зручна обгортка для отримання температури у градусах Цельсія через LUT.
 *
 * @param lut Вказівник на таблицю LUT
 * @param resistance_ohm Виміряний опір у Омах (Ом)
 * @param temp_c Вихідна температура в градусах Цельсія (°C)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_lut_lookup_temp_c(const rtd_lut_t *lut, double resistance_ohm, double *temp_c);

#endif /* RTD_LUT_H */
