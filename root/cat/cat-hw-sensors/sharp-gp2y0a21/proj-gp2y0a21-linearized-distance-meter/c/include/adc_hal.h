/**
 * @file adc_hal.h
 * @brief Апаратний рівень абстракції (HAL) для аналогово-цифрового перетворювача (АЦП).
 *
 * Оголошує структури, типи даних та функції для налаштування периферії АЦП,
 * вибору часу накопичення заряду (Sampling Time) та виконання синхронного/неблокуючого
 * зчитування напруги з аналогових каналів мікроконтролера.
 */

#ifndef ADC_HAL_H
#define ADC_HAL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Максимальна кількість підтримуваних каналів АЦП */
#define ADC_HAL_MAX_CHANNELS 8

/** Тип ідентифікатора аналогового каналу */
typedef uint8_t adc_channel_t;

/**
 * @brief Перелік роздільної здатності АЦП
 */
typedef enum {
    ADC_RES_10BIT = 10, /**< 10-бітний режим (0..1023) */
    ADC_RES_12BIT = 12  /**< 12-бітний режим (0..4095) */
} adc_resolution_t;

/**
 * @brief Перелік тривалості накопичення заряду (Sampling Time)
 *
 * Тривалий час вибірки необхідний для джерел з високим вихідним імпедансом,
 * таких як аналоговий вихід ІЧ-далекоміра Sharp GP2Y0A21YK0F.
 */
typedef enum {
    ADC_SAMPLETIME_SHORT = 0,  /**< Короткий час вибірки (~1.5-15 тактів) */
    ADC_SAMPLETIME_MEDIUM = 1, /**< Середній час вибірки (~28-56 тактів) */
    ADC_SAMPLETIME_LONG = 2    /**< Тривалий час вибірки (>84 тактів, рекомендовано для GP2Y0A21) */
} adc_sampling_time_t;

/**
 * @brief Коди повернення АЦП HAL
 */
typedef enum {
    ADC_OK = 0,                  /**< Успішне виконання операції */
    ADC_ERROR_INVALID_PARAM = -1, /**< Передано невалідні параметри */
    ADC_ERROR_TIMEOUT = -2,       /**< Таймаут виконання перетворення */
    ADC_ERROR_BUSY = -3,          /**< Периферія зайнята іншим перетворенням */
    ADC_ERROR_NOT_INITIALIZED = -4 /**< Канал АЦП не ініціалізовано */
} adc_status_t;

/**
 * @brief Конфігурація аналогового каналу АЦП
 */
typedef struct {
    adc_channel_t channel_id;          /**< Номер каналу АЦП (0..ADC_HAL_MAX_CHANNELS-1) */
    adc_resolution_t resolution;        /**< Роздільна здатність (10 або 12 біт) */
    adc_sampling_time_t sampling_time; /**< Тривалість вибірки сигналу */
    float vref_volts;                   /**< Опорна напруга АЦП у вольтах (наприклад, 3.3V або 5.0V) */
    uint32_t gpio_pin;                  /**< Номер аналогового виводу GPIO */
} adc_config_t;

/**
 * @brief Ініціалізація каналу АЦП з заданими параметрами конфігурації.
 *
 * @param channel Номер каналу АЦП.
 * @param config Вказівник на структуру конфігурації каналу.
 * @return ADC_OK у разі успіху або відповідний код помилки.
 */
adc_status_t adc_hal_init(adc_channel_t channel, const adc_config_t *config);

/**
 * @brief Синхронне (блокуюче) зчитування сирого цифрового значення АЦП.
 *
 * @param channel Номер каналу АЦП.
 * @param raw_value Вказівник для збереження отриманого цифрового коду АЦП.
 * @return ADC_OK у разі успіху або код помилки.
 */
adc_status_t adc_hal_read_raw_blocking(adc_channel_t channel, uint16_t *raw_value);

/**
 * @brief Запуск асинхронного (неблокуючого) перетворення АЦП.
 *
 * @param channel Номер каналу АЦП.
 * @return ADC_OK у разі успішного старту перетворення.
 */
adc_status_t adc_hal_start_non_blocking(adc_channel_t channel);

/**
 * @brief Перевірка готовності та зчитування результату асинхронного перетворення.
 *
 * @param channel Номер каналу АЦП.
 * @param raw_value Вказівник для збереження результату АЦП.
 * @param is_ready Вказівник на прапорець завершення перетворення.
 * @return ADC_OK у разі успіху.
 */
adc_status_t adc_hal_get_non_blocking_result(adc_channel_t channel, uint16_t *raw_value, bool *is_ready);

/**
 * @brief Перетворення сирого цифрового значення АЦП у напругу у вольтах.
 *
 * @param raw_value Сирий цифровий код АЦП.
 * @param resolution Роздільна здатність АЦП (10-біт або 12-біт).
 * @param vref_volts Опорна напруга АЦП у вольтах.
 * @return Обчислена аналогова напруга у вольтах.
 */
float adc_hal_raw_to_voltage(uint16_t raw_value, adc_resolution_t resolution, float vref_volts);

/**
 * @brief Отримання максимального значення цифрового коду для обраної роздільної здатності.
 *
 * @param resolution Роздільна здатність АЦП.
 * @return Максимальний кодовий еквівалент (1023 для 10 біт, 4095 для 12 біт).
 */
uint16_t adc_hal_get_max_value(adc_resolution_t resolution);

#ifdef __cplusplus
}
#endif

#endif /* ADC_HAL_H */
