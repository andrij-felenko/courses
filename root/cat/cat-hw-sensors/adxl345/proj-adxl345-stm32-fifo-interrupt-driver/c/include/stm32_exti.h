#ifndef STM32_EXTI_H
#define STM32_EXTI_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file stm32_exti.h
 * @brief Модуль налаштування та обробки зовнішніх переривань EXTI для STM32.
 */

/**
 * @brief Налаштування апаратної лінії EXTI.
 */
typedef struct {
    void     *gpio_port;   /* Порт GPIO (наприклад, GPIOA) */
    uint16_t  gpio_pin;    /* Номер піна (наприклад, GPIO_PIN_4) */
    uint8_t   irq_channel; /* Номер лінії переривання NVIC */
} stm32_exti_config_t;

/**
 * @brief Ініціалізувати лінію GPIO/EXTI для сигналів INT1/INT2.
 */
void stm32_exti_init(const stm32_exti_config_t *config);

/**
 * @brief Перевірити наявність прапорця переривання Watermark.
 */
bool stm32_exti_has_watermark_flag(void);

/**
 * @brief Скинути прапорець переривання Watermark.
 */
void stm32_exti_clear_watermark_flag(void);

/**
 * @brief Апаратний обробник ISR, викликається з Vector Table STM32.
 */
void stm32_exti_gpio_isr_handler(uint16_t gpio_pin);

#endif /* STM32_EXTI_H */
