#ifndef MCU_ADC_GPIO_H
#define MCU_ADC_GPIO_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file mcu_adc_gpio.h
 * @brief Апаратна абстракція низького рівня для зчитування АЦП та цифрових входів/виходів.
 */

#ifdef __cplusplus
extern "C" {
#endif

#define MCU_GPIO_DIR_INPUT  0
#define MCU_GPIO_DIR_OUTPUT 1

/**
 * @brief Ініціалізація виводу GPIO.
 */
bool mcu_gpio_init(uint8_t pin, uint8_t direction);

/**
 * @brief Зчитування цифрового стану GPIO.
 */
bool mcu_gpio_read(uint8_t pin);

/**
 * @brief Запис цифрового стану у вивід GPIO.
 */
bool mcu_gpio_write(uint8_t pin, bool state);

/**
 * @brief Ініціалізація периферийного модуля АЦП.
 */
bool mcu_adc_init(void);

/**
 * @brief Зчитування відліку з аналогового каналу АЦП.
 */
bool mcu_adc_read_raw(uint8_t channel, uint16_t *out_val);

/* Емуляційні функції для програмного тестування давачів */
void mcu_sim_set_adc_raw(uint8_t channel, uint16_t raw_val);
void mcu_sim_set_gpio(uint8_t pin, bool state);
bool mcu_sim_get_gpio(uint8_t pin);

#ifdef __cplusplus
}
#endif

#endif /* MCU_ADC_GPIO_H */
