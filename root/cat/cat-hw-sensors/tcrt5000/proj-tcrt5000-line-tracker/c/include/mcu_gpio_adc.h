/**
 * @file mcu_gpio_adc.h
 * @brief Апаратний рівень абстракції (HAL) мікроконтролера для GPIO та АЦП.
 *
 * Оголошує інтерфейс для зчитування дискретних сигналів з компараторів LM393
 * та аналогових напруг фототранзисторів давачів TCRT5000.
 */

#ifndef MCU_GPIO_ADC_H
#define MCU_GPIO_ADC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Максимальна кількість підтримуваних каналів АЦП */
#define MCU_ADC_MAX_CHANNELS 8

/** Максимальна роздільна здатність 12-бітного АЦП */
#define MCU_ADC_MAX_VALUE 4095

/**
 * @brief Статуси операцій HAL
 */
typedef enum {
    MCU_OK = 0,
    MCU_ERROR_INVALID_PARAM = -1,
    MCU_ERROR_NULL_POINTER = -2,
    MCU_ERROR_NOT_INITIALIZED = -3,
    MCU_ERROR_HARDWARE_FAILURE = -4
} mcu_status_t;

/**
 * @brief Структура опису піна GPIO
 */
typedef struct {
    uint8_t port_id;  /**< Ідентифікатор порта (наприклад, 0=PortA, 1=PortB) */
    uint8_t pin_num;  /**< Номер піна (0..15) */
} gpio_pin_t;

/**
 * @brief Структура опису каналу АЦП
 */
typedef struct {
    uint8_t channel_id;  /**< Індекс каналу АЦП (0..MCU_ADC_MAX_CHANNELS-1) */
    uint8_t sample_time; /**< Умовний час вибірки АЦП в тактах */
} adc_channel_t;

/**
 * @brief Ініціалізація виводу GPIO у режим цифрового входу.
 * @param pin Структура опису піна.
 * @return MCU_OK у разі успіху, інакше код помилки.
 */
mcu_status_t mcu_gpio_init_input(gpio_pin_t pin);

/**
 * @brief Зчитування логічного рівня з виводу GPIO.
 * @param pin Структура опису піна.
 * @param out_val Вказівник для збереження стану (true - HIGH, false - LOW).
 * @return MCU_OK у разі успіху.
 */
mcu_status_t mcu_gpio_read_pin(gpio_pin_t pin, bool *out_val);

/**
 * @brief Ініціалізація каналу АЦП.
 * @param channel Структура опису каналу АЦП.
 * @return MCU_OK у разі успіху.
 */
mcu_status_t mcu_adc_init_channel(adc_channel_t channel);

/**
 * @brief Однократне зчитування аналогового значення з каналу АЦП (12-біт, 0..4095).
 * @param channel Структура опису каналу АЦП.
 * @param out_raw Вказівник для збереження значення.
 * @return MCU_OK у разі успіху.
 */
mcu_status_t mcu_adc_read_raw(adc_channel_t channel, uint16_t *out_raw);

/**
 * @brief Багатоканальне усреднене зчитування АЦП для зниження високочастотного шуму.
 * @param channels Масив каналів АЦП.
 * @param count Кількість каналів.
 * @param oversample_count Кількість усреднюваних вибірок (наприклад, 4 або 8).
 * @param out_buffer Масив для збереження усреднених результатів.
 * @return MCU_OK у разі успіху.
 */
mcu_status_t mcu_adc_read_multi_oversampled(const adc_channel_t *channels,
                                             uint8_t count,
                                             uint8_t oversample_count,
                                             uint16_t *out_buffer);

#ifdef __cplusplus
}
#endif

#endif /* MCU_GPIO_ADC_H */
