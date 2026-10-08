/**
 * @file mcu_power_exti.h
 * @brief Апаратний рівень абстракції (HAL) для керування живленням МК, GPIO та EXTI.
 *
 * Оголошує низькорівневі функції ініціалізації вхідних/вихідних пінів, конфігурації
 * зовнішнього переривання за зростаючим фронтом (Rising Edge) та переведення
 * мікроконтролера в енергоефективні режими глибокого сну (Deep Sleep / STOP Mode).
 */

#ifndef MCU_POWER_EXTI_H
#define MCU_POWER_EXTI_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Умовні позначення пінів периферії мікроконтролера */
#define MCU_PIR_GPIO_PORT        0xA0U
#define MCU_PIR_GPIO_PIN         0x00U  /**< PA0 — вхідний пін HC-SR505 (EXTI Line 0) */

#define MCU_MOSFET_GPIO_PORT     0xA0U
#define MCU_MOSFET_GPIO_PIN      0x01U  /**< PA1 — вихідний пін керування затвором N-MOSFET */

/**
 * @brief Режими енергоспоживання мікроконтролера.
 */
typedef enum {
    MCU_POWER_MODE_RUN = 0,     /**< Активний режим: ядро та периферія тактуються */
    MCU_POWER_MODE_SLEEP,       /**< Ззвичайний сон: ядро зупинено, периферія працює */
    MCU_POWER_MODE_DEEP_SLEEP   /**< Глибокий сон: тактування ядра й більшості блоків вимкнено, пробудження по EXTI */
} mcu_power_mode_t;

/**
 * @brief Ініціалізація вхідного GPIO виводу для HC-SR505 у режимі Pull-Down.
 * @return true якщо ініціалізація успішна, false у разі апаратної помилки.
 */
bool mcu_gpio_init_pir_input(void);

/**
 * @brief Ініціалізація вихідного GPIO виводу для затвора MOSFET (Push-Pull, Speed Low).
 * @return true якщо ініціалізація успішна.
 */
bool mcu_gpio_init_mosfet_output(void);

/**
 * @brief Налаштування зовнішнього переривання EXTI за зростаючим фронтом (Rising Edge).
 * @param[in] isr_callback Вказівник на C-функцію зворотного виклику, що буде викликана з ISR.
 * @return true якщо переривання успішно сконфігуровано.
 */
bool mcu_exti_init_pir_interrupt(void (*isr_callback)(void));

/**
 * @brief Зчитування поточного фізичного логічного рівня з піну HC-SR505.
 * @return true — логічна 1 (3.3V), false — логічний 0 (0V).
 */
bool mcu_gpio_read_pir_pin(void);

/**
 * @brief Встановлення логічного рівня на затворі N-канального MOSFET.
 * @param[in] level true — встановлює HIGH (V_GS > V_th, відкриває транзистор), false — LOW.
 */
void mcu_gpio_write_mosfet_pin(bool level);

/**
 * @brief Переведення ядра мікроконтролера в режим глибокого сну (Deep Sleep / WFI).
 *
 * У цьому режимі енергоспоживання знижується до мікроампер. Процесор прокидається
 * автоматично при спрацьовуванні EXTI-переривання від HC-SR505.
 */
void mcu_power_enter_deep_sleep(void);

/**
 * @brief Очищення прапора незавершеного переривання EXTI.
 */
void mcu_power_clear_exti_flag(void);

/**
 * @brief Симуляція / отримання поточного системного лічильника часу в мілісекундах.
 * @return Значення системних тиків (мс).
 */
uint32_t mcu_get_tick_ms(void);

/**
 * @brief Затримка виконання у мілісекундах.
 * @param[in] ms Тривалість затримки.
 */
void mcu_delay_ms(uint32_t ms);

/**
 * @brief Симуляція апаратного генератора подій руху (для демонстраційних і тестових цілей).
 */
void mcu_simulate_pir_hardware_event(bool high_level);

#ifdef __cplusplus
}
#endif

#endif /* MCU_POWER_EXTI_H */
