/**
 * @file i2c_driver.h
 * @brief Оголошення низькорівневого C-інтерфейсу I2C для STM32.
 *
 * Забезпечує двобайтовий обмін даними (16-бітні регістри) з корекцією порядку байтів.
 */

#ifndef I2C_DRIVER_H
#define I2C_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди помилок шини I2C.
 */
typedef enum {
    I2C_OK          = 0,  /**< Операція успішна */
    I2C_ERR_START   = 1,  /**< Помилка згенерованого START */
    I2C_ERR_ADDR    = 2,  /**< Пристрій не відповів (NACK на адресу) */
    I2C_ERR_TX      = 3,  /**< Помилка передачі байта */
    I2C_ERR_RX      = 4,  /**< Помилка прийому байта */
    I2C_ERR_TIMEOUT = 5,  /**< Перевищено час очікування прапорця */
    I2C_ERR_BUSY    = 6   /**< Шина I2C зайнята іншим майстром */
} i2c_status_t;

/**
 * @brief Апаратне конфігурування модуля I2C1 у режимі Master.
 * @param clock_speed_hz Частота SCL у Гц (100000 = Standard, 400000 = Fast).
 * @return I2C_OK при успішній ініціалізації.
 */
i2c_status_t i2c1_init(uint32_t clock_speed_hz);

/**
 * @brief Запис 16-бітного слова у регістр веденого чипа INA226 (Big-Endian на шині).
 * @param dev_addr 7-бітна адреса пристрою на шині I2C.
 * @param reg_addr 8-бітна адреса цільового регістра.
 * @param value 16-бітне значення для запису.
 * @return I2C_OK у разі успіху.
 */
i2c_status_t i2c_write_reg16(uint8_t dev_addr, uint8_t reg_addr, uint16_t value);

/**
 * @brief Читання 16-бітного слова з регістра INA226 (Big-Endian у Little-Endian).
 * @param dev_addr 7-бітна адреса пристрою на шині I2C.
 * @param reg_addr 8-бітна адреса цільового регістра.
 * @param value Вказівник для збереження зчитаного 16-бітного слова.
 * @return I2C_OK у разі успіху.
 */
i2c_status_t i2c_read_reg16(uint8_t dev_addr, uint8_t reg_addr, uint16_t *value);

#ifdef __cplusplus
}
#endif

#endif /* I2C_DRIVER_H */
