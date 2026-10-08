/**
 * @file mems_capacitive.h
 * @brief Оголошення інтерфейсу драйвера ємнісного MEMS-сенсора.
 *
 * Файл містить визначення типів даних, структур конфігурації,
 * контексту вимірювань та прототипи функцій для керування протифазним
 * збудженням, калібрування зсуву нуля ЦАП та обробки відгуку.
 */

#ifndef MEMS_CAPACITIVE_H
#define MEMS_CAPACITIVE_H

#include <stdint.h>
#include <stdbool.h>
#include "mems_mcu_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди статусу виконання операцій драйвера MEMS.
 */
typedef enum {
    MEMS_OK = 0,                 /**< Успішне виконання */
    MEMS_ERR_INVALID_ARG = -1,   /**< Передано недійсний аргумент (NULL або поза діапазоном) */
    MEMS_ERR_HAL_FAIL = -2,      /**< Помилка апаратного рівня HAL */
    MEMS_ERR_CALIB_TIMEOUT = -3, /**< Таймаут автокалібрування зсуву нуля */
    MEMS_ERR_SATURATION = -4,    /**< Насичення підсилювача відгуку АЦП */
    MEMS_ERR_NOT_INIT = -5       /**< Драйвер не ініціалізовано */
} mems_status_t;

/**
 * @brief Стани процедури автокалібрування нульового рівня.
 */
typedef enum {
    MEMS_CALIB_UNINITIALIZED = 0, /**< Калібрування ще не виконувалось */
    MEMS_CALIB_IN_PROGRESS,       /**< Процес бінарного пошуку нуля ЦАП */
    MEMS_CALIB_SUCCESS,           /**< Калібрування успішно завершено */
    MEMS_CALIB_FAILED             /**< Калібрування завершилось помилкою */
} mems_calib_state_t;

/**
 * @brief Структура конфігурації диференціального ємнісного контуру.
 */
typedef struct {
    uint32_t excitation_freq_hz;  /**< Частота таккового збудження (Гц) */
    uint16_t num_samples_avg;     /**< Кількість вибірок для усереднення одного вимірювання */
    uint16_t calib_max_iterations;/**< Максимальна кількість ітерацій підбору ЦАП */
    float alpha_filter;           /**< Коефіцієнт експоненціального фільтра EMA (0.0 < alpha <= 1.0) */
    float sensitivity_lsb_per_ff; /**< Чутливість тракту (код АЦП на фемтофарад, LSB/fF) */
    float vref_mv;                /**< Опорна напруга АЦП/ЦАП (мВ) */
} mems_config_t;

/**
 * @brief Структура контексту (пристрою) ємнісного MEMS-сенсора.
 */
typedef struct {
    mems_config_t config;          /**< Налаштування дифконтуру */
    uint16_t dac_zero_offset_raw;  /**< Підібране цифрове значення ЦАП для зсуву нуля */
    mems_calib_state_t calib_state;/**< Поточний стан автокалібрування */
    int32_t raw_phase_0_accum;     /**< Накопичений код АЦП для прямій фази 0° */
    int32_t raw_phase_180_accum;   /**< Накопичений код АЦП для інверсній фази 180° */
    float diff_voltage_mv;         /**< Розрахована різниця напруг фаз dV (мВ) */
    float capacitance_diff_ff;     /**< Поточне значення різниці ємностей dC (fF) */
    float filtered_cap_diff_ff;    /**< Відфільтрована різниця ємностей dC_filt (fF) */
    bool is_initialized;           /**< Прапорець успішної ініціалізації пристрою */
} mems_dev_t;

/**
 * @brief Ініціалізація C-драйвера MEMS-сенсора та підпорядкованої периферії.
 *
 * @param dev Вказівник на об'єкт контексту MEMS-пристрою.
 * @param config Вказівник на структуру конфігурації.
 * @return MEMS_OK у разі успіху, інакше відповідний код помилки.
 */
mems_status_t mems_init(mems_dev_t *dev, const mems_config_t *config);

/**
 * @brief Процедура автокалібрування нульового рівня MEMS-структури у стані спокою.
 *
 * Використовує метод бінарного пошуку (діхотомії) для вибору коду ЦАП (DAC),
 * який компенсує початкову технологічну асиметрію ємностей C1 та C2.
 *
 * @param dev Вказівник на контекст MEMS-пристрою.
 * @return MEMS_OK у разі успішного калібрування, інакше код помилки.
 */
mems_status_t mems_calibrate_zero(mems_dev_t *dev);

/**
 * @brief Синхронне зчитування сирого різницевого сигналу при протифазному збудженні.
 *
 * @param dev Вказівник на контекст MEMS-пристрою.
 * @param diff_raw Вказівник для збереження обчисленої різниці коду (Phase0 - Phase180).
 * @return MEMS_OK у разі успіху, інакше код помилки.
 */
mems_status_t mems_read_differential_raw(mems_dev_t *dev, int32_t *diff_raw);

/**
 * @brief Повний цикл обробки одного вимірювального відліку (зчитування + конверсія + EMA фільтрація).
 *
 * @param dev Вказівник на контекст MEMS-пристрою.
 * @return MEMS_OK у разі успіху, інакше код помилки.
 */
mems_status_t mems_process_sample(mems_dev_t *dev);

/**
 * @brief Отримання поточного значення різниці ємностей (dC) у фемтофарадах.
 *
 * @param dev Вказівник на контекст MEMS-пристрою.
 * @param cap_diff_ff Вказівник для збереження результату dC (fF).
 * @return MEMS_OK або код помилки.
 */
mems_status_t mems_get_capacitance_diff(const mems_dev_t *dev, float *cap_diff_ff);

/**
 * @brief Отримання відфільтрованого значення різниці ємностей у фемтофарадах.
 *
 * @param dev Вказівник на контекст MEMS-пристрою.
 * @param filtered_ff Вказівник для збереження відфільтрованого результату (fF).
 * @return MEMS_OK або код помилки.
 */
mems_status_t mems_get_filtered_capacitance(const mems_dev_t *dev, float *filtered_ff);

#ifdef __cplusplus
}
#endif

#endif /* MEMS_CAPACITIVE_H */
