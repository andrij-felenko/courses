#ifndef ADC_CURRENT_SENSOR_H
#define ADC_CURRENT_SENSOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file adc_current_sensor.h
 * @brief Модуль оцифрування та обробки сигналу струму з токовимірювального шунта.
 *
 * Забезпечує накопичення вибірок АЦП у кільцевому буфері, цифрову фільтрацію
 * методом ковзного середнього та обчислення середньоквадратичного струму (RMS) у мА.
 */

#define ADC_SENSOR_BUFFER_SIZE  32U     /**< Розмір кільцевого буфера вибірок */
#define ADC_SENSOR_MAX_RAW      4095.0f /**< Максимальне значення 12-бітного АЦП */

/**
 * @brief Структура опису та стану сенсора струму АЦП
 */
typedef struct {
    float shunt_resistor_ohms;                 /**< Опір вимірювального шунта (Ом) */
    float amplifier_gain;                      /**< Коефіцієнт підсилення підсилювача/ОП */
    float reference_voltage_v;                 /**< Опорна напруга АЦП (Вольт) */

    uint16_t raw_samples[ADC_SENSOR_BUFFER_SIZE]; /**< Кільцевий буфер сирих вибірок АЦП */
    size_t head_index;                         /**< Поточна позиція запису в буфері */
    size_t sample_count;                       /**< Кількість накопичених вибірок */
    uint32_t raw_sum;                          /**< Сума поточних вибірок для швидкого згладжування */

    float last_instant_ma;                     /**< Останній миттєвий струм у міліамперах */
    float last_rms_ma;                         /**< Останнє обчислене значення RMS струму в мА */
    uint32_t last_update_ms;                   /**< Часова мітка останнього оновлення (мс) */
} adc_sensor_t;

/**
 * @brief Ініціалізує сенсор струму та обнуляє внутрішні буфери.
 * @param sensor Вказівник на структуру сенсора
 * @param shunt_resistor_ohms Опір шунта в Омах (наприклад, 0.1 або 0.05)
 * @param gain Коефіцієнт підсилення схеми (наприклад, 10.0 або 1.0)
 * @param ref_voltage_v Опорна напруга АЦП (наприклад, 3.3)
 * @return 0 у разі успіху, -1 при некоректних параметрах
 */
int adc_sensor_init(adc_sensor_t *sensor, float shunt_resistor_ohms, float gain, float ref_voltage_v);

/**
 * @brief Додає нову сиру вибірку АЦП до кільцевого буфера.
 * @param sensor Вказівник на структуру сенсора
 * @param raw_adc Сире значення з АЦП (0..4095)
 * @param timestamp_ms Поточний час у мілісекундах
 */
void adc_sensor_push_sample(adc_sensor_t *sensor, uint16_t raw_adc, uint32_t timestamp_ms);

/**
 * @brief Обчислює та повертає середньоквадратичне значення струму (RMS) у міліамперах.
 * @param sensor Вказівник на структуру сенсора
 * @return Значення RMS струму у мА
 */
float adc_sensor_calculate_rms(adc_sensor_t *sensor);

/**
 * @brief Повертає поточне миттєве значення струму у міліамперах.
 * @param sensor Вказівник на структуру сенсора
 * @return Миттєвий струм у мА
 */
float adc_sensor_get_instant_ma(const adc_sensor_t *sensor);

/**
 * @brief Очищає кільцевий буфер та скидає статистику накопичення.
 * @param sensor Вказівник на структуру сенсора
 */
void adc_sensor_reset_buffer(adc_sensor_t *sensor);

#endif /* ADC_CURRENT_SENSOR_H */
