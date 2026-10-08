#ifndef LVDT_H
#define LVDT_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "adc_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @file lvdt.h
 * @brief Модуль обробки сигналів Лінійного Змінного Диференціального Трансформатора (LVDT).
 *
 * Описує типи даних, структури конфігурації та прототипи функцій для перетворення
 * напруги аналогового кондиціонера LVDT у фізичне лінійне переміщення, калібрування
 * нуля, цифрової фільтрації EMA та діагностики несправностей.
 */

/** Стандартне значення коефіцієнта фільтрації EMA (0 < alpha <= 1) */
#define LVDT_DEFAULT_EMA_ALPHA         0.20f

/** Стандартна кількість вибірок для автоматичного калібрування нуля */
#define LVDT_DEFAULT_CALIB_SAMPLES     32

/**
 * @brief Статуси вимірювання та діагностики LVDT
 */
typedef enum {
    LVDT_OK                     =  0,  /**< Вимірювання успішне, сигнал у межах норми */
    LVDT_WARN_OUT_OF_RANGE_MIN  =  1,  /**< Переміщення нижче мінімальної межі робочого ходу */
    LVDT_WARN_OUT_OF_RANGE_MAX  =  2,  /**< Переміщення вище максимальної межі робочого ходу */
    LVDT_ERROR_NULL_POINTER     = -1,  /**< Передано нульовий вказівник */
    LVDT_ERROR_INVALID_PARAM    = -2,  /**< Некоректні параметри конфігурації */
    LVDT_ERROR_NOT_INITIALIZED  = -3,  /**< Драйвер не ініціалізовано */
    LVDT_ERROR_ADC              = -4,  /**< Помилка зчитування даних з АЦП */
    LVDT_ERROR_SIGNAL_FAULT     = -5   /**< Аварія сигналу (обрив кабелю або коротке замикання) */
} lvdt_status_t;

/**
 * @brief Конфігурація LVDT-сенсора та параметрів обробки
 */
typedef struct {
    adc_channel_t adc_channel;         /**< Аналоговий канал АЦП */
    adc_resolution_t adc_resolution;   /**< Роздільна здатність АЦП */
    adc_sampling_time_t sample_time;   /**< Тривалість вибірки АЦП */
    float vref_volts;                  /**< Опорна напруга АЦП VREF (В) */
    float sensitivity_mm_per_v;        /**< Коефіцієнт чутливості S (мм/В) */
    float min_displacement_mm;         /**< Мінімальна робоча межа переміщення (мм) */
    float max_displacement_mm;         /**< Максимальна робоча межа переміщення (мм) */
    float min_valid_voltage_v;         /**< Нижня межа допустимої напруги (для виявлення обриву, В) */
    float max_valid_voltage_v;         /**< Верхня межа допустимої напруги (для виявлення КЗ/насичення, В) */
    float filter_alpha;                /**< Коефіцієнт EMA фільтрації (0.0 < alpha <= 1.0) */
} lvdt_config_t;

/**
 * @brief Структура виміряних та розрахованих даних LVDT
 */
typedef struct {
    uint16_t raw_adc;                  /**< Останній сирий код АЦП */
    float raw_voltage_v;               /**< Миттєва зчитана напруга (В) */
    float filtered_voltage_v;          /**< Згладжена напруга після EMA (В) */
    float displacement_mm;             /**< Обчислене фізичне переміщення сердечника (мм) */
    lvdt_status_t status;              /**< Статус вимірювання та діагностики */
} lvdt_reading_t;

/**
 * @brief Контекст дескриптора LVDT-драйвера
 */
typedef struct {
    lvdt_config_t config;              /**< Копія налаштувань сенсора */
    float zero_offset_volts;           /**< Напруга нульового положення V_zero (В) */
    float filtered_voltage_v;          /**< Внутрішній стан фільтра EMA */
    bool is_zero_calibrated;           /**< Прапор проходження калібрування нуля */
    bool is_initialized;               /**< Прапор успішної ініціалізації драйвера */
} lvdt_t;

/**
 * @brief Ініціалізація драйвера LVDT та налаштування АЦП.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param config Вказівник на структуру конфігурації.
 * @return LVDT_OK або відповідний код помилки.
 */
lvdt_status_t lvdt_init(lvdt_t *dev, const lvdt_config_t *config);

/**
 * @brief Процедура автокалібрування нульового зсуву (Zero Offset Calibration).
 *
 * Виконує серію вибірок у центрі робочого ходу сердечника та визначає V_zero.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param num_samples Кількість замірів для усереднення (наприклад, 16..64).
 * @return LVDT_OK або код помилки зчитування АЦП.
 */
lvdt_status_t lvdt_calibrate_zero(lvdt_t *dev, uint16_t num_samples);

/**
 * @brief Ручне встановлення напруги нуля (наприклад, із збережених у NVM/EEPROM даних).
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param zero_volts Значення напруги нуля у Вольтах.
 * @return LVDT_OK або LVDT_ERROR_INVALID_PARAM.
 */
lvdt_status_t lvdt_set_zero_offset(lvdt_t *dev, float zero_volts);

/**
 * @brief Зчитування миттєвої сирої напруги з аналогового кондиціонера LVDT.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param voltage_out Вказівник для збереження напруги (В).
 * @return LVDT_OK або код помилки.
 */
lvdt_status_t lvdt_read_raw_voltage(lvdt_t *dev, float *voltage_out);

/**
 * @brief Застосування цифрового фільтра експоненційного ковзного усереднення (EMA).
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param new_voltage Нове значення напруги.
 * @return Оновлена відфільтрована напруга.
 */
float lvdt_apply_ema_filter(lvdt_t *dev, float new_voltage);

/**
 * @brief Обчислення фізичного лінійного переміщення за напругою та коефіцієнтом чутливості.
 *
 * Формула: displacement_mm = (voltage_v - zero_offset_volts) * sensitivity_mm_per_v.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param voltage_v Напруга сигналу.
 * @param displacement_mm Вказівник для збереження зміщення у мм.
 * @return LVDT_OK або код помилки.
 */
lvdt_status_t lvdt_convert_voltage_to_displacement(const lvdt_t *dev, float voltage_v, float *displacement_mm);

/**
 * @brief Валідація напруги та лінійного переміщення на вихід за межі та обрив лінії.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param voltage_v Виміряна напруга.
 * @param displacement_mm Розраховане зміщення.
 * @return LVDT_OK, LVDT_WARN_OUT_OF_RANGE_MIN, LVDT_WARN_OUT_OF_RANGE_MAX або LVDT_ERROR_SIGNAL_FAULT.
 */
lvdt_status_t lvdt_validate_signal(const lvdt_t *dev, float voltage_v, float displacement_mm);

/**
 * @brief Повний цикл опрацювання вибірки: зчитування АЦП, EMA-фільтрація, розрахунок переміщення та діагностика.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 * @param reading Вказівник на структуру результату вимірювання.
 * @return Статус виконання обробки.
 */
lvdt_status_t lvdt_process_sample(lvdt_t *dev, lvdt_reading_t *reading);

/**
 * @brief Скидання внутрішнього стану EMA-фільтра до поточного нуля.
 *
 * @param dev Вказівник на екземпляр LVDT-контексту.
 */
void lvdt_reset_filter(lvdt_t *dev);

#ifdef __cplusplus
}
#endif

#endif /* LVDT_H */
