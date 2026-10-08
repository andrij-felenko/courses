#ifndef STM32_GPIO_EXTI_H
#define STM32_GPIO_EXTI_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Призначення GPIO пінів для трьох давачів Холла SS41F (Порт GPIOB).
 * Hall A -> PB0 (EXTI0)
 * Hall B -> PB1 (EXTI1)
 * Hall C -> PB2 (EXTI2)
 */
#define HALL_PIN_A_BIT       0U
#define HALL_PIN_B_BIT       1U
#define HALL_PIN_C_BIT       2U

#define HALL_PIN_A_MASK      (1U << HALL_PIN_A_BIT)
#define HALL_PIN_B_MASK      (1U << HALL_PIN_B_BIT)
#define HALL_PIN_C_MASK      (1U << HALL_PIN_C_BIT)

#define HALL_PINS_ALL_MASK   (HALL_PIN_A_MASK | HALL_PIN_B_MASK | HALL_PIN_C_MASK)

/**
 * @brief Макрос швидкого зчитування 3-бітового коду з регістру вхідних даних IDR.
 * 
 * Формує триплет (A << 2) | (B << 1) | C із пінів PB0, PB1, PB2.
 */
#define STM32_READ_HALL_RAW_CODE(idr_val) \
    ((((idr_val) & HALL_PIN_A_MASK) >> HALL_PIN_A_BIT << 2) | \
     (((idr_val) & HALL_PIN_B_MASK) >> HALL_PIN_B_BIT << 1) | \
     (((idr_val) & HALL_PIN_C_MASK) >> HALL_PIN_C_BIT))

/**
 * @brief Тип зворотного виклику для обробника переривань EXTI.
 * 
 * Передає 3-бітовий raw_code у контексті ISR без затримок.
 */
typedef void (*stm32_exti_isr_callback_t)(uint8_t raw_code);

/**
 * @brief Ініціалізація периферії GPIO, EXTI та NVIC для ліній SS41F.
 */
void stm32_gpio_exti_init(void);

/**
 * @brief Пряме атомарне зчитування вхідних пінів Hall A, B, C з регістру IDR.
 * 
 * @return uint8_t 3-бітовий код стан-триплета (0..7)
 */
uint8_t stm32_gpio_read_hall_pins(void);

/**
 * @brief Реєстрація функції зворотного виклику для апаратного ISR.
 * 
 * @param cb Функція-обробник переривання EXTI
 */
void stm32_exti_register_callback(stm32_exti_isr_callback_t cb);

#ifdef __cplusplus
}
#endif

#endif /* STM32_GPIO_EXTI_H */
