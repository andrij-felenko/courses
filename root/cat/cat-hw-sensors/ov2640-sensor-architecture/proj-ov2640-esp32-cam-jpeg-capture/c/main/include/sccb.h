#ifndef SCCB_H
#define SCCB_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

#define SCCB_I2C_PORT       0         /**< Апаратний порт I2C мікроконтролера ESP32 */
#define OV2640_SCCB_ADDR    0x30      /**< 7-бітна I2C адреса сенсора OV2640 (8-бітне значення 0x60 >> 1) */

#define SCCB_REG_BANK_SEL   0xFF      /**< Регістр вибору банку регістрів (Bank Select Register) */
#define SCCB_BANK_DSP       0x00      /**< Банк регістрів DSP (Digital Signal Processor) */
#define SCCB_BANK_SENSOR    0x01      /**< Банк регістрів Sensor (матриця пікселів та AGC/AEC/AWB) */

/**
 * @brief Ініціалізація шини SCCB на базі периферії I2C ESP-IDF у режимі Master.
 *
 * @param sda_pin Номер GPIO для лінії даних SIOD/SDA.
 * @param scl_pin Номер GPIO для лінії тактування SIOC/SCL.
 * @param freq_hz Частота шини I2C у Гц (за замовчуванням 100000 Гц).
 * @return ESP_OK у разі успішної ініціалізації, код помилки ESP-IDF у разі збою.
 */
esp_err_t sccb_init(int sda_pin, int scl_pin, uint32_t freq_hz);

/**
 * @brief Деініціалізація та звільнення ресурсів контролера I2C.
 *
 * @return ESP_OK у разі успіху.
 */
esp_err_t sccb_deinit(void);

/**
 * @brief Запис 8-бітного значення у вказаний регістр пристрою через шину SCCB.
 *
 * @param slv_addr 7-бітна адреса SCCB пристрою.
 * @param reg Адреса регістру.
 * @param val Значення для запису.
 * @return ESP_OK у разі успішного підтвердження ACK, інакше код помилки.
 */
esp_err_t sccb_write_reg(uint8_t slv_addr, uint8_t reg, uint8_t val);

/**
 * @brief Зчитування 8-бітного значення з регістру пристрою через шину SCCB.
 *
 * @param slv_addr 7-бітна адреса SCCB пристрою.
 * @param reg Адреса регістру для зчитання.
 * @param val Вказівник для збереження прочитаного значення.
 * @return ESP_OK у разі успіху, інакше код помилки.
 */
esp_err_t sccb_read_reg(uint8_t slv_addr, uint8_t reg, uint8_t *val);

/**
 * @brief Перемикання активного банку регістрів OV2640 (DSP Bank 0x00 або Sensor Bank 0x01).
 *
 * @param slv_addr 7-бітна адреса SCCB пристрою.
 * @param bank Значення банку (SCCB_BANK_DSP або SCCB_BANK_SENSOR).
 * @return ESP_OK у разі успішного запису в регістр 0xFF.
 */
esp_err_t sccb_set_bank(uint8_t slv_addr, uint8_t bank);

#ifdef __cplusplus
}
#endif

#endif /* SCCB_H */
