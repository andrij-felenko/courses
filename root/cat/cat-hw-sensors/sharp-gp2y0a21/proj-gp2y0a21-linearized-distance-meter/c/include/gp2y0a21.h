/**
 * @file gp2y0a21.h
 * @brief Драйвер аналогового інфрачервоного триангуляційного далекоміра Sharp GP2Y0A21YK0F.
 *
 * Модуль реалізує інтерфейс для ініціалізації сенсора, збору серії вибірок,
 * програмної медіанної фільтрації шумів, обчислення відстані за нелінійною
 * характеристикою d = A / (ADC - B) та перевірки межових значень (10–80 см).
 */

#ifndef GP2Y0A21_H
#define GP2Y0A21_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "adc_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

/** Паспортний мінімальний робочий поріг відстані (см) */
#define GP2Y0A21_MIN_DISTANCE_CM 10.0f

/** Паспортний максимальний робочий поріг відстані (см) */
#define GP2Y0A21_MAX_DISTANCE_CM 80.0f

/** Замовчувана кількість вибірок для медіанної фільтрації */
#define GP2Y0A21_DEFAULT_SAMPLE_COUNT 5

/** Максимально допустима кількість вибірок у масиві фільтрації */
#define GP2Y0A21_MAX_SAMPLE_COUNT 15

/**
 * Замовчувані коефіцієнти лінеаризації для 12-бітного АЦП та VREF = 3.3V:
 * Формула: distance_cm = COEFF_A / (ADC_raw - COEFF_B)
 */
#define GP2Y0A21_DEFAULT_COEFF_A 26960.0f
#define GP2Y0A21_DEFAULT_COEFF_B 159.0f

/**
 * @brief Статуси виконання операцій драйвера Sharp GP2Y0A21YK0F
 */
typedef enum {
    GP2Y0A21_OK = 0,                          /**< Вимірювання успішне та в межах діапазону */
    GP2Y0A21_ERROR_NULL_POINTER = -1,         /**< Передано нульовий вказівник */
    GP2Y0A21_ERROR_INVALID_PARAM = -2,        /**< Некоректні параметри конфігурації */
    GP2Y0A21_ERROR_ADC_READ = -3,             /**< Помилка зчитання даних з АЦП */
    GP2Y0A21_OUT_OF_BOUNDS_TOO_CLOSE = -4,    /**< Об'єкт занадто близько (< 10 см або зона пікової невизначеності) */
    GP2Y0A21_OUT_OF_BOUNDS_TOO_FAR = -5       /**< Об'єкт занадто далеко (> 80 см) */
} gp2y0a21_status_t;

/**
 * @brief Конфігурація драйвера Sharp GP2Y0A21YK0F
 */
typedef struct {
    adc_channel_t adc_channel;   /**< Канал АЦП мікроконтролера */
    uint8_t sample_count;        /**< Кількість вибірок для медіанного фільтра (рекомендовано 5..9) */
    float coeff_a;               /**< Коефіцієнт лінеаризації A у формулі d = A / (ADC - B) */
    float coeff_b;               /**< Зсув B у формулі d = A / (ADC - B) */
    float min_distance_cm;       /**< Нижня межа робочого діапазону (за замовчуванням 10.0 см) */
    float max_distance_cm;       /**< Верхня межа робочого діапазону (за замовчуванням 80.0 см) */
} gp2y0a21_config_t;

/**
 * @brief Результат вимірювання відстані та телеметрії
 */
typedef struct {
    uint16_t raw_adc_median;     /**< Медіанно-фільтроване сире значення АЦП */
    float voltage_v;             /**< Відповідна напруга у вольтах на аналоговому виході VOUT */
    float distance_cm;           /**< Розрахована відстань у сантиметрах */
    gp2y0a21_status_t status;    /**< Статус вимірювання (ОК або вихід за межі) */
} gp2y0a21_reading_t;

/**
 * @brief Дескриптор екземпляра драйвера далекоміра
 */
typedef struct {
    gp2y0a21_config_t config;    /**< Конфігурація екземпляра */
    adc_resolution_t resolution; /**< Роздільна здатність використаного АЦП */
    float vref_volts;            /**< Опорна напруга АЦП */
    bool is_initialized;         /**< Прапор успішної ініціалізації */
} gp2y0a21_t;

/**
 * @brief Ініціалізація драйвера далекоміра Sharp GP2Y0A21YK0F.
 *
 * @param dev Вказівник на дескриптор пристрою.
 * @param config Вказівник на конфігураційну структуру.
 * @param resolution Роздільна здатність АЦП.
 * @param vref_volts Опорна напруга АЦП.
 * @return GP2Y0A21_OK у разі успіху або код помилки.
 */
gp2y0a21_status_t gp2y0a21_init(gp2y0a21_t *dev, const gp2y0a21_config_t *config, adc_resolution_t resolution, float vref_volts);

/**
 * @brief Зчитування серії незгладжених вибірок з АЦП.
 *
 * @param dev Вказівник на дескриптор пристрою.
 * @param samples_out Масив для збереження сирих вибірок АЦП.
 * @param count Кількість замірів для зчитування.
 * @return GP2Y0A21_OK у разі успіху.
 */
gp2y0a21_status_t gp2y0a21_read_samples(gp2y0a21_t *dev, uint16_t *samples_out, uint8_t count);

/**
 * @brief Обчислення медіани з масиву вибірок АЦП.
 *
 * Створює локальну копію масиву, сортує її та повертає центральне значення,
 * що дозволяє придушити поодинокі імпульсні шуми та сплески напруги.
 *
 * @param samples Масив вибірок.
 * @param count Кількість елементів масиву.
 * @return Згладжене медіанне значення АЦП.
 */
uint16_t gp2y0a21_filter_median(uint16_t *samples, uint8_t count);

/**
 * @brief Обчислення фізичної відстані у сантиметрах за сирим кодом АЦП.
 *
 * Застосовує формулу лінеаризації: d = A / (ADC_raw - B).
 *
 * @param dev Вказівник на дескриптор пристрою.
 * @param adc_raw Медіанне значення АЦП.
 * @param distance_out Вказівник для збереження розрахованої відстані.
 * @return GP2Y0A21_OK або статус виходу за межі / помилка обчислень.
 */
gp2y0a21_status_t gp2y0a21_convert_to_distance(const gp2y0a21_t *dev, uint16_t adc_raw, float *distance_out);

/**
 * @brief Перевірка належності відстані до паспортного робочого діапазону (10–80 см).
 *
 * @param dev Вказівник на дескриптор пристрою.
 * @param distance_cm Розрахована відстань у см.
 * @return GP2Y0A21_OK, GP2Y0A21_OUT_OF_BOUNDS_TOO_CLOSE або GP2Y0A21_OUT_OF_BOUNDS_TOO_FAR.
 */
gp2y0a21_status_t gp2y0a21_validate_bounds(const gp2y0a21_t *dev, float distance_cm);

/**
 * @brief Виконання повного циклу вимірювання: збір вибірок, медіанна фільтрація,
 *        лінеаризація та перевірка межових значень.
 *
 * @param dev Вказівник на дескриптор пристрою.
 * @param reading Вказівник на структуру результату вимірювання.
 * @return Статус результату вимірювання.
 */
gp2y0a21_status_t gp2y0a21_read_distance(gp2y0a21_t *dev, gp2y0a21_reading_t *reading);

#ifdef __cplusplus
}
#endif

#endif /* GP2Y0A21_H */
