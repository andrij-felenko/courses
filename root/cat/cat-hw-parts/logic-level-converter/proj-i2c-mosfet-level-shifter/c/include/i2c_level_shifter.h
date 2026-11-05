#ifndef I2C_LEVEL_SHIFTER_H
#define I2C_LEVEL_SHIFTER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "driver/i2c.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Робоча частота шини I2C з урахуванням затримок транзисторів BSS138.
 */
typedef enum {
    I2C_SPEED_STANDARD_100K = 100000, ///< Стандартний режим (100 кГц, t_r до 1000 нс)
    I2C_SPEED_FAST_400K     = 400000  ///< Швидкісний режим (400 кГц, t_r до 300 нс)
} i2c_bus_speed_t;

/**
 * @brief Конфігураційні параметри для роботи з перетворювачем рівнів.
 */
typedef struct {
    i2c_port_t port;              ///< Апаратний порт I2C (I2C_NUM_0 або I2C_NUM_1)
    int sda_pin;                  ///< Номер виводу SDA мікроконтролера (сторона 3.3 В)
    int scl_pin;                  ///< Номер виводу SCL мікроконтролера (сторона 3.3 В)
    i2c_bus_speed_t speed_hz;     ///< Тактова частота передачі
    bool enable_internal_pullup;  ///< Дозвіл вбудованої підтяжки (false при наявності 10 кОм на платі транслятора)
    uint32_t timeout_ms;          ///< Граничний тайм-аут очікування відповіді веденого пристрою
} i2c_shifter_config_t;

/**
 * @brief Ініціалізація апаратного контролера I2C у режимі відкритого стоку.
 *
 * @param cfg Вказівник на структуру параметрів шини.
 * @return esp_err_t ESP_OK при успіху або відповідний код помилки ESP-IDF.
 */
esp_err_t i2c_shifter_init(const i2c_shifter_config_t *cfg);

/**
 * @brief Запис даних у регістр 5-вольтового веденого пристрою через MOSFET-транслятор.
 *
 * @param cfg Конфігурація підключення.
 * @param dev_addr 7-бітний адрес 5 В пристрою на шині.
 * @param reg_addr Адреса внутрішнього регістра.
 * @param data Вказівник на масив байтів для передачі.
 * @param len Кількість байтів для запису.
 * @return esp_err_t ESP_OK, ESP_ERR_TIMEOUT або ESP_FAIL у разі отримання NACK.
 */
esp_err_t i2c_shifter_write_reg(const i2c_shifter_config_t *cfg,
                                uint8_t dev_addr,
                                uint8_t reg_addr,
                                const uint8_t *data,
                                size_t len);

/**
 * @brief Зчитування телеметрії з регістра 5-вольтового пристрою.
 *
 * @param cfg Конфігурація підключення.
 * @param dev_addr 7-бітний адрес веденого 5 В давача.
 * @param reg_addr Початковий регістр для читання.
 * @param data Буфер для збереження отриманих даних.
 * @param len Кількість байтів для зчитування.
 * @return esp_err_t ESP_OK, ESP_ERR_TIMEOUT або ESP_FAIL.
 */
esp_err_t i2c_shifter_read_reg(const i2c_shifter_config_t *cfg,
                               uint8_t dev_addr,
                               uint8_t reg_addr,
                               uint8_t *data,
                               size_t len);

/**
 * @brief Звільнення ресурсів драйвера I2C.
 *
 * @param port Номер порту I2C для деініціалізації.
 * @return esp_err_t ESP_OK при успішному закритті.
 */
esp_err_t i2c_shifter_deinit(i2c_port_t port);

#ifdef __cplusplus
}
#endif

#endif // I2C_LEVEL_SHIFTER_H
