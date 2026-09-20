#ifndef STICK_DRIFT_FILTER_H
#define STICK_DRIFT_FILTER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @file stick_drift_filter.h
 * @brief Модуль калібрування, EMA-фільтрації та радіальної мертвої зони для аналогових джойстиків.
 */

/**
 * @brief Структура зафіксованих калібрувальних параметрів двоосьового джойстика
 */
typedef struct {
    uint16_t center_x;      /**< Сирий відлік АЦП у нейтральному стані по осі X */
    uint16_t center_y;      /**< Сирий відлік АЦП у нейтральному стані по осі Y */
    uint16_t min_x;         /**< Мінімальний відлік АЦП при крайньому відхиленні ліворуч */
    uint16_t max_x;         /**< Максимальний відлік АЦП при крайньому відхиленні праворуч */
    uint16_t min_y;         /**< Мінімальний відлік АЦП при крайньому відхиленні донизу */
    uint16_t max_y;         /**< Максимальний відлік АЦП при крайньому відхиленні догори */
} stick_calibration_t;

/**
 * @brief Нормалізовані векторні координати осі джойстика після обробки (-1.0 ... 1.0)
 */
typedef struct {
    float x;                /**< Згладжена нормована координата X [-1.0f, 1.0f] */
    float y;                /**< Згладжена нормована координата Y [-1.0f, 1.0f] */
    float magnitude;        /**< Довжина радіального вектора [0.0f, 1.0f] */
} stick_output_t;

/**
 * @brief Конфігурація та дескриптор стану фільтра компенсації дрейфу
 */
typedef struct {
    stick_calibration_t cal; /**< Калібрувальні дані осей */
    float deadzone_inner;   /**< Внутрішній радіус мертвої зони (наприклад, 0.10f = 10%) */
    float deadzone_outer;   /**< Зовнішній поріг насичення (наприклад, 0.95f = 95%) */
    float ema_alpha;        /**< Коефіцієнт згладжування EMA (0.0f < alpha <= 1.0f) */
    
    /* Внутрішній стан EMA-фільтра */
    float filtered_x;       /**< Останнє відфільтроване значення X */
    float filtered_y;       /**< Останнє відфільтроване значення Y */
    bool is_initialized;    /**< Прапорець первинної ініціалізації EMA */
} stick_filter_t;

/**
 * @brief Ініціалізація дескриптора фільтра джойстика
 * @param filter Вказівник на дескриптор фільтра
 * @param cal Вказівник на структуру калібрування
 * @param deadzone_inner Внутрішня мертва зона (0.0f ... 0.5f)
 * @param deadzone_outer Зовнішній поріг насичення (0.5f ... 1.0f)
 * @param ema_alpha Коефіцієнт EMA-фільтра (0.05f ... 1.0f)
 * @return true при успішній ініціалізації, false при хибних аргументах
 */
bool stick_filter_init(stick_filter_t *filter, 
                      const stick_calibration_t *cal, 
                      float deadzone_inner, 
                      float deadzone_outer, 
                      float ema_alpha);

/**
 * @brief Автоматичне зчитування та фіксація нейтральних точок осей (калібрування дрейфу нуля)
 * @param cal Вказівник на структуру калібрування
 * @param raw_x_samples Масив відліків АЦП осі X
 * @param raw_y_samples Масив відліків АЦП осі Y
 * @param sample_count Кількість вибірок
 * @return true при успішній фіксації нейтралі
 */
bool stick_calibrate_center(stick_calibration_t *cal, 
                             const uint16_t *raw_x_samples, 
                             const uint16_t *raw_y_samples, 
                             size_t sample_count);

/**
 * @brief Повний цикл неблокуючої обробки сирих відліків АЦП (EMA -> Нормалізація -> Scaled Radial Deadzone)
 * @param filter Вказівник на ініціалізований дескриптор фільтра
 * @param raw_x Сирий відлік АЦП осі X
 * @param raw_y Сирий відлік АЦП осі Y
 * @param out Вихідна структура з нормалізованими координатами
 */
void stick_filter_process(stick_filter_t *filter, 
                         uint16_t raw_x, 
                         uint16_t raw_y, 
                         stick_output_t *out);

#ifdef __cplusplus
}
#endif

#endif /* STICK_DRIFT_FILTER_H */
