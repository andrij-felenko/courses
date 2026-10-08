#ifndef MCU_PWM_GPIO_H
#define MCU_PWM_GPIO_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file mcu_pwm_gpio.h
 * @brief Оголошення низькорівневого апаратного інтерфейсу мікроконтролера (GPIO, ШІМ, затримки).
 */

/**
 * @brief Логічні рівні на виводах GPIO мікроконтролера.
 */
typedef enum {
    MCU_GPIO_LOW  = 0,  /**< Логічний нуль (0 В) */
    MCU_GPIO_HIGH = 1   /**< Логічна одиниця (VCC) */
} mcu_gpio_state_t;

/**
 * @brief Статусні коди виконання операцій низькорівневого периферійного модуля.
 */
typedef enum {
    MCU_OK              =  0,  /**< Операція успішна */
    MCU_ERR_INVALID_ARG = -1,  /**< Передано некоректні аргументи */
    MCU_ERR_HW_FAULT    = -2   /**< Апаратний збій периферії */
} mcu_err_t;

/**
 * @brief Конфігураційна структура апаратного ШІМ-таймера.
 */
typedef struct {
    uint32_t frequency_hz;   /**< Цільова частота ШІМ у Герцах (наприклад, 20000 Гц) */
    uint32_t prescaler;      /**< Значення дільника частоти таймера (PSC) */
    uint32_t auto_reload_arr;/**< Значення регістру автоматичного перезавантаження (ARR) */
    uint8_t  pwm_channel;    /**< Номер каналу ШІМ (1..4) */
} mcu_pwm_config_t;

/* --- Прототипи функцій керування GPIO --- */

/**
 * @brief Ініціалізація цифрового виводу GPIO у режим Push-Pull Output.
 * @param pin Номер виводу GPIO.
 * @return MCU_OK у разі успіху.
 */
mcu_err_t mcu_gpio_init_output(uint8_t pin);

/**
 * @brief Встановлення логічного рівня на виводі GPIO.
 * @param pin Номер виводу GPIO.
 * @param state Логічний рівень (MCU_GPIO_LOW або MCU_GPIO_HIGH).
 * @return MCU_OK у разі успіху.
 */
mcu_err_t mcu_gpio_write(uint8_t pin, mcu_gpio_state_t state);

/**
 * @brief Зчитування поточного логічного стану виводу GPIO.
 * @param pin Номер виводу GPIO.
 * @param out_state Вказівник для збереження значення.
 * @return MCU_OK у разі успіху.
 */
mcu_err_t mcu_gpio_read(uint8_t pin, mcu_gpio_state_t *out_state);

/* --- Прототипи функцій керування апаратним ШІМ --- */

/**
 * @brief Ініціалізація апаратного ШІМ-таймера з розрахунком регістрів PSC та ARR.
 * @param config Вказівник на конфігураційну структуру ШІМ.
 * @return MCU_OK у разі успішного налаштування.
 */
mcu_err_t mcu_pwm_init(mcu_pwm_config_t *config);

/**
 * @brief Встановлення коефіцієнта заповнення ШІМ у відсотках (0..100%).
 * @param channel Номер каналу ШІМ.
 * @param duty_percent Коефіцієнт заповнення у відсотках.
 * @return MCU_OK у разі успіху.
 */
mcu_err_t mcu_pwm_set_duty_cycle(uint8_t channel, uint8_t duty_percent);

/**
 * @brief Запис точного значення порівняння в регістр CCR каналу ШІМ.
 * @param channel Номер каналу ШІМ.
 * @param ccr_val Значення для регістру CCR.
 * @return MCU_OK у разі успіху.
 */
mcu_err_t mcu_pwm_set_ccr_value(uint8_t channel, uint32_t ccr_val);

/**
 * @brief Зупинка та вимкнення виходу ШІМ-каналу.
 * @param channel Номер каналу ШІМ.
 * @return MCU_OK у разі успіху.
 */
mcu_err_t mcu_pwm_stop(uint8_t channel);

/* --- Системні затримки часу --- */

/**
 * @brief Точна мікросекундна затримка (використовується для генерації Dead Time).
 * @param us Кількість мікросекунд.
 */
void mcu_delay_us(uint32_t us);

/**
 * @brief Мілісекундна системна затримка.
 * @param ms Кількість мілісекунд.
 */
void mcu_delay_ms(uint32_t ms);

#endif /* MCU_PWM_GPIO_H */
