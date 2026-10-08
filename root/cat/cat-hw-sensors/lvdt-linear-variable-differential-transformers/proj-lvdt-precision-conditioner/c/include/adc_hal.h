#ifndef ADC_HAL_H
#define ADC_HAL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @file adc_hal.h
 * @brief Апаратний рівень абстракції (HAL) АЦП для зчитування аналогового сигналу LVDT.
 *
 * Модуль визначає конфігурацію роздільної здатності АЦП, каналів вибірки,
 * часу накопичення заряду (Sampling Time) та надає інтерфейси оцифрування.
 */

/**
 * @brief Роздільна здатність аналогово-цифрового перетворювача (біти)
 */
typedef enum {
    ADC_RES_8BIT  = 8,   /**< 8-бітний режим (0..255) */
    ADC_RES_10BIT = 10,  /**< 10-бітний режим (0..1023) */
    ADC_RES_12BIT = 12,  /**< 12-бітний режим (0..4095) */
    ADC_RES_14BIT = 14,  /**< 14-бітний режим (0..16383) */
    ADC_RES_16BIT = 16   /**< 16-бітний режим (0..65535) */
} adc_resolution_t;

/**
 * @brief Канали аналогового входу мікроконтролера
 */
typedef enum {
    ADC_CHANNEL_0 = 0,   /**< Аналоговий канал 0 */
    ADC_CHANNEL_1,       /**< Аналоговий канал 1 */
    ADC_CHANNEL_2,       /**< Аналоговий канал 2 */
    ADC_CHANNEL_3,       /**< Аналоговий канал 3 */
    ADC_CHANNEL_MAX
} adc_channel_t;

/**
 * @brief Час вибірки АЦП (в тактах) для узгодження з імпедансом джерела
 */
typedef enum {
    ADC_SAMPLETIME_1_5_CYCLES = 0,  /**< 1.5 тактів (для низькоімпедансних джерел) */
    ADC_SAMPLETIME_7_5_CYCLES,      /**< 7.5 тактів */
    ADC_SAMPLETIME_13_5_CYCLES,     /**< 13.5 тактів */
    ADC_SAMPLETIME_28_5_CYCLES,     /**< 28.5 тактів */
    ADC_SAMPLETIME_55_5_CYCLES,     /**< 55.5 тактів */
    ADC_SAMPLETIME_239_5_CYCLES     /**< 239.5 тактів (рекомендовано для LVDT кондиціонерів з високим імпедансом) */
} adc_sampling_time_t;

/**
 * @brief Коди статусів виконання HAL АЦП
 */
typedef enum {
    ADC_OK                  =  0,  /**< Операція успішна */
    ADC_ERROR_INVALID_PARAM = -1,  /**< Некоректний параметр */
    ADC_ERROR_TIMEOUT       = -2,  /**< Перевищено час очікування оцифрування */
    ADC_ERROR_HARDWARE      = -3   /**< Апаратна помилка периферії АЦП */
} adc_status_t;

/**
 * @brief Конфігураційна структура периферії АЦП
 */
typedef struct {
    adc_channel_t channel;          /**< Працюючий аналоговий канал */
    adc_resolution_t resolution;    /**< Обрана роздільна здатність */
    adc_sampling_time_t sample_time;/**< Тривалість вибірки сигналу */
    float vref_volts;               /**< Опорна напруга VREF (Вольти) */
} adc_config_t;

/**
 * @brief Ініціалізація апаратного модуля АЦП.
 *
 * @param config Вказівник на конфігураційну структуру АЦП.
 * @return ADC_OK у разі успішного налаштування.
 */
adc_status_t adc_hal_init(const adc_config_t *config);

/**
 * @brief Оцифрування одного значення з вказаного аналогового каналу.
 *
 * @param channel Номер аналогового каналу.
 * @param raw_value Вказівник для збереження сирого цифрового коду АЦП.
 * @return ADC_OK у разі успіху.
 */
adc_status_t adc_hal_read_raw(adc_channel_t channel, uint16_t *raw_value);

/**
 * @brief Серійне оцифрування декількох вибірок підряд (блокуючий режим або DMA).
 *
 * @param channel Номер аналогового каналу.
 * @param buffer Масив для збереження цифрових кодингів.
 * @param count Кількість замірів.
 * @return ADC_OK у разі успіху.
 */
adc_status_t adc_hal_read_raw_multiple(adc_channel_t channel, uint16_t *buffer, uint16_t count);

/**
 * @brief Перетворення сирого цифрового коду АЦП у напругу в вольтах.
 *
 * @param raw_value Значення з виходу АЦП.
 * @param resolution Роздільна здатність АЦП.
 * @param vref_volts Опорна напруга АЦП.
 * @return Перерахована напруга у вольтах.
 */
float adc_hal_raw_to_voltage(uint16_t raw_value, adc_resolution_t resolution, float vref_volts);

/**
 * @brief Обчислення максимально можливого коду АЦП для заданої роздільної здатності.
 *
 * @param resolution Роздільна здатність АЦП.
 * @return Максимальний код (наприклад, 4095 для 12 біт).
 */
uint32_t adc_hal_get_max_code(adc_resolution_t resolution);

#ifdef __cplusplus
}
#endif

#endif /* ADC_HAL_H */
