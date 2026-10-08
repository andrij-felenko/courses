#ifndef RTD_LUT_H
#define RTD_LUT_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "rtd_sensor.h"

/**
 * @file rtd_lut.h
 * @brief Модуль табличного пошуку (LUT) та лінійної інтерполяції для датчиків RTD.
 *
 * Оптимізований алгоритм розрахунку температури для мікроконтролерів без
 * апаратного блоку плаваючої коми (FPU) або при підвищених вимогах до швидкодії.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Елемент таблиці Look-Up Table (LUT) для Pt100.
 */
typedef struct {
    float temp_c;          /**< Температура (°C) */
    float resistance_ohms; /**< Номінальний опір Pt100 при цій температурі (Ом) */
} rtd_lut_entry_t;

/* --- Параметри статичної таблиці LUT для Pt100 (-200 °C .. +850 °C з кроком 50 °C) --- */
#define RTD_LUT_MIN_TEMP      -200.0f
#define RTD_LUT_MAX_TEMP       850.0f
#define RTD_LUT_STEP_TEMP       50.0f
#define RTD_LUT_SIZE            22

/**
 * @brief Опорна таблиця опорів Pt100 за IEC 60751 від -200 °C до +850 °C.
 */
static const rtd_lut_entry_t g_rtd_pt100_lut[RTD_LUT_SIZE] = {
    { -200.0f,  18.52f },
    { -150.0f,  39.72f },
    { -100.0f,  60.26f },
    {  -50.0f,  80.31f },
    {    0.0f, 100.00f },
    {   50.0f, 119.40f },
    {  100.0f, 138.51f },
    {  150.0f, 157.33f },
    {  200.0f, 175.86f },
    {  250.0f, 194.10f },
    {  300.0f, 212.05f },
    {  350.0f, 229.72f },
    {  400.0f, 247.09f },
    {  450.0f, 264.18f },
    {  500.0f, 280.98f },
    {  550.0f, 297.49f },
    {  600.0f, 313.71f },
    {  650.0f, 329.64f },
    {  700.0f, 345.28f },
    {  750.0f, 360.64f },
    {  800.0f, 375.70f },
    {  850.0f, 390.48f }
};

/**
 * @brief Пошук температури за опором методом лінійної інтерполяції плаваючої коми.
 * @param resistance_ohms Обчислений опір (Ом).
 * @param r0_ohms Номінальний опір при 0 °C (100.0 для Pt100 або 1000.0 для Pt1000).
 * @param out_temp_c Результат розрахованої температури (°C).
 * @return Статус діагностики RTD.
 */
static inline rtd_status_t rtd_lut_resistance_to_temp_float(float resistance_ohms, 
                                                            float r0_ohms, 
                                                            float *out_temp_c) {
    if (out_temp_c == NULL || r0_ohms <= 0.0f) {
        return RTD_STATUS_ERR_PARAM;
    }

    /* Нормалізація опору до еквівалента Pt100 (якщо вимірюється Pt1000) */
    float norm_r = resistance_ohms * (RTD_PT100_R0 / r0_ohms);

    /* Перевірка меж */
    if (norm_r < g_rtd_pt100_lut[0].resistance_ohms) {
        if (norm_r < g_rtd_pt100_lut[0].resistance_ohms * 0.5f) {
            *out_temp_c = RTD_MIN_TEMP_C;
            return RTD_STATUS_ERR_SHORT_CIRCUIT;
        }
        *out_temp_c = RTD_MIN_TEMP_C;
        return RTD_STATUS_ERR_OUT_OF_RANGE;
    }

    if (norm_r > g_rtd_pt100_lut[RTD_LUT_SIZE - 1].resistance_ohms) {
        if (norm_r > g_rtd_pt100_lut[RTD_LUT_SIZE - 1].resistance_ohms * 1.15f) {
            *out_temp_c = RTD_MAX_TEMP_C;
            return RTD_STATUS_ERR_OPEN_CIRCUIT;
        }
        *out_temp_c = RTD_MAX_TEMP_C;
        return RTD_STATUS_ERR_OUT_OF_RANGE;
    }

    /* Бінарний пошук інтервалу в LUT */
    size_t low = 0;
    size_t high = RTD_LUT_SIZE - 1;

    while (high - low > 1) {
        size_t mid = (low + high) / 2;
        if (g_rtd_pt100_lut[mid].resistance_ohms <= norm_r) {
            low = mid;
        } else {
            high = mid;
        }
    }

    /* Лінійна інтерполяція: T = T0 + (R_norm - R0) * (T1 - T0) / (R1 - R0) */
    float r0 = g_rtd_pt100_lut[low].resistance_ohms;
    float r1 = g_rtd_pt100_lut[high].resistance_ohms;
    float t0 = g_rtd_pt100_lut[low].temp_c;
    float t1 = g_rtd_pt100_lut[high].temp_c;

    *out_temp_c = t0 + (norm_r - r0) * (t1 - t0) / (r1 - r0);
    return RTD_STATUS_OK;
}

/**
 * @brief Оптимізована реалізація у фіксованій крапці для мікроконтролерів без FPU.
 * @param resistance_mOhms Опір у міліомах (Ом * 1000).
 * @param r0_mOhms Номінальний опір у міліомах (100000 для Pt100).
 * @param out_temp_mC Вихідна температура в міліградусах Цельсія (°C * 1000).
 * @return Статус виконання.
 */
static inline rtd_status_t rtd_lut_resistance_to_temp_fixed(uint32_t resistance_mOhms, 
                                                            uint32_t r0_mOhms, 
                                                            int32_t *out_temp_mC) {
    if (out_temp_mC == NULL || r0_mOhms == 0) {
        return RTD_STATUS_ERR_PARAM;
    }

    /* Нормалізація до масштабу Pt100 у міліомах (100000 мОм) */
    uint64_t norm_r = ((uint64_t)resistance_mOhms * 100000ULL) / r0_mOhms;

    uint32_t min_r_mOhm = (uint32_t)(g_rtd_pt100_lut[0].resistance_ohms * 1000.0f);
    uint32_t max_r_mOhm = (uint32_t)(g_rtd_pt100_lut[RTD_LUT_SIZE - 1].resistance_ohms * 1000.0f);

    if (norm_r < min_r_mOhm) {
        *out_temp_mC = -200000;
        return RTD_STATUS_ERR_SHORT_CIRCUIT;
    }
    if (norm_r > max_r_mOhm) {
        *out_temp_mC = 850000;
        return RTD_STATUS_ERR_OPEN_CIRCUIT;
    }

    /* Пошук сегмента та обчислення цілочисельної інтерполяції */
    for (size_t i = 0; i < RTD_LUT_SIZE - 1; i++) {
        uint32_t r_low = (uint32_t)(g_rtd_pt100_lut[i].resistance_ohms * 1000.0f);
        uint32_t r_high = (uint32_t)(g_rtd_pt100_lut[i + 1].resistance_ohms * 1000.0f);

        if (norm_r >= r_low && norm_r <= r_high) {
            int32_t t_low = (int32_t)(g_rtd_pt100_lut[i].temp_c * 1000.0f);
            int32_t t_high = (int32_t)(g_rtd_pt100_lut[i + 1].temp_c * 1000.0f);

            uint32_t delta_r = r_high - r_low;
            int32_t delta_t = t_high - t_low;

            uint32_t offset_r = (uint32_t)norm_r - r_low;
            *out_temp_mC = t_low + (int32_t)(((int64_t)offset_r * delta_t) / delta_r);
            return RTD_STATUS_OK;
        }
    }

    *out_temp_mC = 0;
    return RTD_STATUS_ERR_OUT_OF_RANGE;
}

#ifdef __cplusplus
}
#endif

#endif /* RTD_LUT_H */
