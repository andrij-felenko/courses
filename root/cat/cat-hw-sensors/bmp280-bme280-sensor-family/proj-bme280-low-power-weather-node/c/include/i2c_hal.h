#ifndef I2C_HAL_H
#define I2C_HAL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file i2c_hal.h
 * @brief Оголошення апаратного рівня абстракції (HAL) шини I2C мікроконтролера.
 * 
 * Надає прототипи функцій ініціалізації периферійного модуля I2C у режимі Master,
 * транзакційного читання/запису поодиноких регістрів та послідовного читання (burst read)
 * за 7-бітною адресою пристрою BME280 (0x76 / 0x77).
 */

#define I2C_HAL_DEFAULT_TIMEOUT_MS  100  /*!< Базовий таймаут шинної транзакції (мс) */

/**
 * @brief Статуси операцій I2C HAL
 */
typedef enum {
    I2C_HAL_OK                   =  0,  /*!< Транзакція виконана успішно */
    I2C_HAL_ERR_NULL_PTR         = -1,  /*!< Передано некоректний вказівник */
    I2C_HAL_ERR_TIMEOUT          = -2,  /*!< Перевищення часу очікування прапорця шини */
    I2C_HAL_ERR_NACK             = -3,  /*!< Отримано сигнал відсутності квитування (NACK) */
    I2C_HAL_ERR_BUS_BUSY         = -4,  /*!< Шина I2C зайнята іншим майстром */
    I2C_HAL_ERR_ARBITRATION_LOST = -5   /*!< Втрата арбітражу на шині */
} i2c_hal_err_t;

/**
 * @brief Ініціалізація периферійного модуля I2C мікроконтролера в режимі Master.
 * @param clock_speed_hz Частота тактування шини в Гц (100000 для Standard Mode, 400000 для Fast Mode).
 * @return I2C_HAL_OK у разі успішної конфігурації периферії.
 */
i2c_hal_err_t i2c_hal_init(uint32_t clock_speed_hz);

/**
 * @brief Запис одного байта у регістр веденого пристрою I2C.
 * @param dev_addr 7-бітна адреса веденого пристрою (0x76 або 0x77).
 * @param reg_addr Адреса регістру пристрою.
 * @param data Байт даних для запису.
 * @return I2C_HAL_OK при підтвердженні прийому (ACK).
 */
i2c_hal_err_t i2c_hal_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t data);

/**
 * @brief Зчитування одного байта з регістру веденого пристрою I2C.
 * @param dev_addr 7-бітна адреса веденого пристрою.
 * @param reg_addr Адреса регістру пристрою.
 * @param out_data Вказівник для збереження прочитаного байта.
 * @return I2C_HAL_OK при успішному зчитуванні.
 */
i2c_hal_err_t i2c_hal_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *out_data);

/**
 * @brief Послідовне (burst) зчитування масиву байтів з пристрою I2C.
 * @param dev_addr 7-бітна адреса веденого пристрою.
 * @param start_reg Початкова адреса регістру.
 * @param buffer Буфер для прийому даних.
 * @param len Кількість байтів для зчитування.
 * @return I2C_HAL_OK при успішному прочитанні всього блоку.
 */
i2c_hal_err_t i2c_hal_read_bytes(uint8_t dev_addr, uint8_t start_reg, uint8_t *buffer, size_t len);

/**
 * @brief Затримка виконання у мілісекундах.
 * @param ms Кількість мілісекунд.
 */
void i2c_hal_delay_ms(uint32_t ms);

/**
 * @brief Отримання поточного значення системного таймера у мілісекундах.
 * @return uint32_t Системний час (мс).
 */
uint32_t i2c_hal_get_ticks_ms(void);

/**
 * @brief Перетворення коду помилки I2C HAL у текстовий рядок.
 * @param err Код помилки.
 * @return const char* Опис помилки українською мовою.
 */
const char* i2c_hal_err_to_str(i2c_hal_err_t err);

#endif /* I2C_HAL_H */
