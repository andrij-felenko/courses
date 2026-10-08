/**
 * @file i2c_hal.h
 * @brief Оголошення низькорівневого апаратного інтерфейсу I2C та GPIO хост-мікроконтролера.
 *
 * Надає незалежний від платформи C HAL шар абстракції для виконання транзакцій I2C,
 * керування цифровими лініями скидання XSHUT і обробки таймерних затримок.
 */

#ifndef I2C_HAL_H
#define I2C_HAL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди повернення апаратного рівня HAL.
 */
typedef enum {
    HAL_I2C_OK       = 0, /**< Операцію виконано успішно */
    HAL_I2C_ERROR    = 1, /**< Помилка обміну або NACK від пристрою */
    HAL_I2C_BUSY     = 2, /**< Шина I2C зайнята */
    HAL_I2C_TIMEOUT  = 3  /**< Перевищено таймаут очікування */
} hal_status_t;

/**
 * @brief Структура опису апаратного виводу GPIO.
 */
typedef struct {
    uint16_t pin_id;      /**< Ідентифікатор/номер виводу GPIO */
    uint32_t port_base;   /**< Базова адреса регістрів порту (наприклад, GPIOA_BASE) */
} hal_gpio_pin_t;

/* ========================================================================== */
/*                             ПРОТОТИПИ I2C HAL                              */
/* ========================================================================== */

/**
 * @brief Ініціалізація апаратного контролера I2C хост-мікроконтролера.
 * @param speed_hz Частота тактування шини в Гц (100000 або 400000 Гц).
 * @return HAL_I2C_OK у разі успіху.
 */
hal_status_t hal_i2c_init(uint32_t speed_hz);

/**
 * @brief Синхронний запис 8-бітного значення в регістр веденого I2C-пристрою.
 * @param dev_addr 7-бітна I2C-адреса.
 * @param reg_addr Адреса внутрішнього регістра.
 * @param value Значення байта для запису.
 * @return Результат виконання транзакції.
 */
hal_status_t hal_i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t value);

/**
 * @brief Синхронне зчитування 8-бітного значення з регістра I2C-пристрою.
 * @param dev_addr 7-бітна I2C-адреса.
 * @param reg_addr Адреса внутрішнього регістра.
 * @param p_value Вказівник для запису прочитаного значення.
 * @return Результат виконання транзакції.
 */
hal_status_t hal_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *p_value);

/**
 * @brief Синхронний послідовний запис масиву байтів у регістр I2C.
 * @param dev_addr 7-бітна I2C-адреса.
 * @param reg_addr Початкова адреса регістра.
 * @param p_data Вказівник на буфер даних.
 * @param len Кількість байтів для запису.
 * @return Результат виконання транзакції.
 */
hal_status_t hal_i2c_write_multi(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *p_data, uint16_t len);

/**
 * @brief Синхронне або DMA/IT зчитування послідовності байтів з регістрів I2C.
 * @param dev_addr 7-бітна I2C-адреса.
 * @param reg_addr Початкова адреса регістра.
 * @param p_data Вказівник на буфер для збереження даних.
 * @param len Кількість байтів для читання.
 * @return Результат виконання транзакції.
 */
hal_status_t hal_i2c_read_multi(uint8_t dev_addr, uint8_t reg_addr, uint8_t *p_data, uint16_t len);

/* ========================================================================== */
/*                             ПРОТОТИПИ GPIO ТА СИСТЕМИ                      */
/* ========================================================================== */

/**
 * @brief Встановлення логічного стану на виводі GPIO.
 * @param pin Структура з описом виводу.
 * @param state true — високий рівень (3.3V), false — низький рівень (0V).
 */
void hal_gpio_write(hal_gpio_pin_t pin, bool state);

/**
 * @brief Затримка виконання поточного потоку в мілісекундах.
 * @param ms Час затримки у мілісекундах.
 */
void hal_delay_ms(uint32_t ms);

/**
 * @brief Зчитання системного таймера системних тіків (мілісекунд).
 * @return Поточний системний час у мс.
 */
uint32_t hal_get_tick_ms(void);

#ifdef __cplusplus
}
#endif

#endif /* I2C_HAL_H */
