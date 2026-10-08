#ifndef RTD_IEC60751_H
#define RTD_IEC60751_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file rtd_iec60751.h
 * @brief Оголошення C-інтерфейсу модуля для роботи з платиновими термоопорами (RTD)
 * відповідно до стандарту IEC 60751.
 */

/* Коефіцієнти рівняння Каллендара — Ван Дюзена за IEC 60751 (ITS-90) */
#define RTD_CVD_A  3.9083e-3     /* Коефіцієнт A (градус Цельсія^-1) */
#define RTD_CVD_B -5.775e-7      /* Коефіцієнт B (градус Цельсія^-2) */
#define RTD_CVD_C -4.183e-12     /* Коефіцієнт C (градус Цельсія^-4, використовується лише для t < 0 °C) */

/* Номінальні опори при 0 °C (Ом) */
#define RTD_PT100_R0   100.0
#define RTD_PT1000_R0 1000.0

/* Межі температурного діапазону за стандартом IEC 60751 (°C) */
#define RTD_TEMP_MIN  -200.0
#define RTD_TEMP_MAX   850.0

/**
 * @brief Типи платинових давачів температури.
 */
typedef enum {
    RTD_TYPE_PT100 = 0,
    RTD_TYPE_PT1000
} rtd_type_t;

/**
 * @brief Класи допуску (точності) за стандартом IEC 60751.
 */
typedef enum {
    RTD_CLASS_AA = 0,  /* Допуск: dT = ±(0.10 + 0.0017 * |t|) °C */
    RTD_CLASS_A,       /* Допуск: dT = ±(0.15 + 0.0020 * |t|) °C */
    RTD_CLASS_B,       /* Допуск: dT = ±(0.30 + 0.0050 * |t|) °C */
    RTD_CLASS_C        /* Допуск: dT = ±(0.60 + 0.0100 * |t|) °C */
} rtd_class_t;

/**
 * @brief Коди статусу та помилок процедурного модуля.
 */
typedef enum {
    RTD_SUCCESS = 0,
    RTD_ERROR_NULL_POINTER,
    RTD_ERROR_INVALID_TYPE,
    RTD_ERROR_INVALID_CLASS,
    RTD_ERROR_OUT_OF_RANGE,
    RTD_ERROR_CONVERGENCE_FAILED
} rtd_status_t;

/**
 * @brief Структура конфігурації RTD-сенсора.
 */
typedef struct {
    rtd_type_t type;         /* Тип сенсора (Pt100 / Pt1000) */
    rtd_class_t tolerance;    /* Клас допуску */
    double r0;               /* Номінальний опір при 0 °C (Ом) */
} rtd_config_t;

/**
 * @brief Ініціалізація структури конфігурації RTD-сенсора.
 *
 * @param config Вказівник на структуру конфігурації
 * @param type Тип давача (Pt100 або Pt1000)
 * @param tolerance_class Клас допуску (AA, A, B або C)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_init(rtd_config_t *config, rtd_type_t type, rtd_class_t tolerance_class);

/**
 * @brief Обчислення опору сенсора за заданою температурою (пряме перетворення CVD).
 *
 * @param config Вказівник на конфігурацію RTD
 * @param temp_c Температура в градусах Цельсія (°C)
 * @param resistance Вихідне значення опору в Омах (Ом)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_temperature_to_resistance(const rtd_config_t *config, double temp_c, double *resistance);

/**
 * @brief Перетворення виміряного опору в температуру методом Ньютона — Рафсона.
 *
 * @param config Вказівник на конфігурацію RTD
 * @param resistance Виміряний опір сенсора (Ом)
 * @param max_error_c Допустима похибка збіжності (°C)
 * @param max_iterations Максимальна кількість ітерацій
 * @param temp_c Вихідна обчислена температура (°C)
 * @param iterations_used Кількість використаних ітерацій (може бути NULL)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_resistance_to_temperature_nr(const rtd_config_t *config,
                                              double resistance,
                                              double max_error_c,
                                              size_t max_iterations,
                                              double *temp_c,
                                              size_t *iterations_used);

/**
 * @brief Обчислення допустимого температурного відхилення за стандартом IEC 60751.
 *
 * @param tolerance_class Клас допуску
 * @param temp_c Температура (°C)
 * @param tolerance_c Вихідне значення допустимого відхилення (°C)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_get_tolerance_c(rtd_class_t tolerance_class, double temp_c, double *tolerance_c);

/**
 * @brief Перевірка відповідності виміряного опору давача його класу допуску.
 *
 * @param config Вказівник на конфігурацію RTD
 * @param resistance Виміряний опір (Ом)
 * @param temp_c Очікувана або виміряна контрольна температура (°C)
 * @param is_valid Вихідний прапорець відповідності класу
 * @param dev_c Вихідне значення відхилення температури від номіналу (°C)
 * @return rtd_status_t Статус виконання
 */
rtd_status_t rtd_validate_tolerance(const rtd_config_t *config,
                                    double resistance,
                                    double temp_c,
                                    bool *is_valid,
                                    double *dev_c);

#endif /* RTD_IEC60751_H */
