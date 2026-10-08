#ifndef I2C_DRIVER_H
#define I2C_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file i2c_driver.h
 * @brief Низькорівневий апаратний інтерфейс шини I2C для мікроконтролера.
 */

/* Швидкість шини I2C */
typedef enum {
    I2C_SPEED_STANDARD = 100000U, /**< Стандартний режим (100 кГц) */
    I2C_SPEED_FAST     = 400000U  /**< Швидкий режим (400 кГц) */
} i2c_speed_t;

/* Коди помилок шини I2C */
typedef enum {
    I2C_OK           =  0, /**< Операція успішна */
    I2C_ERR_TIMEOUT  = -1, /**< Таймаут очікування прапорця готовності шини */
    I2C_ERR_NACK     = -2, /**< Відсутність підтвердження (NACK) від пристрою */
    I2C_ERR_BUSY     = -3, /**< Шина зайнята іншим майстром або заблокована */
    I2C_ERR_PARAM    = -4, /**< Некоректні вхідні параметри */
    I2C_ERR_HALT     = -5  /**< Апаратна відмова модуля I2C */
} i2c_status_t;

/**
 * @brief Ініціалізація апаратного модуля I2C у режимі Master.
 * @param speed Швидкість обміну (100 кГц або 400 кГц).
 * @return I2C_OK у разі успіху, або відповідний код помилки.
 */
i2c_status_t i2c_init(i2c_speed_t speed);

/**
 * @brief Запис послідовності байтів у ведений пристрій I2C.
 * @param dev_addr 7-бітна адреса I2C пристрою.
 * @param data Вказівник на масив даних для відправки.
 * @param len Кількість байтів для запису.
 * @param timeout_ms Максимальний час очікування в мілісекундах.
 * @return I2C_OK у разі успіху, інакше код помилки.
 */
i2c_status_t i2c_write(uint8_t dev_addr, const uint8_t *data, size_t len, uint32_t timeout_ms);

/**
 * @brief Читання послідовності байтів з веденого пристрою I2C.
 * @param dev_addr 7-бітна адреса I2C пристрою.
 * @param data Вказівник на буфер для збереження прийнятих даних.
 * @param len Кількість байтів для читання.
 * @param timeout_ms Максимальний час очікування в мілісекундах.
 * @return I2C_OK у разі успіху, інакше код помилки.
 */
i2c_status_t i2c_read(uint8_t dev_addr, uint8_t *data, size_t len, uint32_t timeout_ms);

/**
 * @brief Запис значення в один регістр веденого пристрою I2C.
 * @param dev_addr 7-бітна адреса I2C пристрою.
 * @param reg_addr Адреса цільового регістра.
 * @param value Значення для запису.
 * @return I2C_OK у разі успіху, інакше код помилки.
 */
i2c_status_t i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t value);

/**
 * @brief Читання значення з одного регістра веденого пристрою I2C.
 * @param dev_addr 7-бітна адреса I2C пристрою.
 * @param reg_addr Адреса цільового регістра.
 * @param value Вказівник на змінну для збереження прочитаного значення.
 * @return I2C_OK у разі успіху, інакше код помилки.
 */
i2c_status_t i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *value);

/**
 * @brief Читання послідовності регістрів веденого пристрою (починаючи з reg_addr).
 * @param dev_addr 7-бітна адреса I2C пристрою.
 * @param reg_addr Початкова адреса регістра.
 * @param buffer Вказівник на буфер даних.
 * @param len Кількість байтів.
 * @return I2C_OK у разі успіху, інакше код помилки.
 */
i2c_status_t i2c_read_regs(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buffer, size_t len);

/**
 * @brief Перевірка наявності пристрою на шині I2C (ping/ack check).
 * @param dev_addr 7-бітна адреса I2C пристрою.
 * @return true, якщо пристрій відповів ACK, false якщо NACK або таймаут.
 */
bool i2c_ping(uint8_t dev_addr);

#endif /* I2C_DRIVER_H */
