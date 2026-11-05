#ifndef EFUSE_FLASH_SECURITY_H
#define EFUSE_FLASH_SECURITY_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "esp_flash_encrypt.h"
#include "esp_secure_boot.h"
#include "esp_efuse.h"
#include "esp_partition.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Розмір блоку шифрування Flash-пам'яті в байтах для апаратного прискорювача AES-XTS в ESP32-S3.
 * Будь-які операції запису в зашифровані розділи мають бути вирівняні по цій межі.
 */
#define FLASH_ENCRYPTION_BLOCK_SIZE 32

/**
 * @brief Структура для збереження статусів апаратних механізмів безпеки ESP32-S3.
 */
typedef struct {
    bool flash_encryption_enabled;   /**< Прапор активності апаратного шифрування Flash-пам'яті */
    esp_flash_enc_mode_t flash_enc_mode; /**< Режим шифрування Flash (Development або Release) */
    bool secure_boot_enabled;        /**< Прапор активності системи Secure Boot V2 */
    bool jtag_disabled;              /**< Прапор відключення апаратного інтерфейсу JTAG в eFuse */
    bool uart_bootloader_disabled;   /**< Прапор відключення/обмеження режимів UART ROM Bootloader */
    bool key_block_read_protected;   /**< Прапор захисту від зчитування ключових блоків eFuse (BLOCK_KEY) */
    bool key_block_write_protected;  /**< Прапор захисту від перезапису ключових блоків eFuse (BLOCK_KEY) */
} efuse_security_status_t;

/**
 * @brief Зчитування поточного стану апаратних засобів безпеки та eFuse-полів ESP32-S3.
 *
 * @param[out] status Вказівник на структуру для запису статусів безпеки.
 * @return esp_err_t ESP_OK у разі успішного зчитування, або код помилки.
 */
esp_err_t efuse_security_read_status(efuse_security_status_t *status);

/**
 * @brief Виведення зведеного звіту про стан безпеки мікроконтролера в консоль логування.
 *
 * @param[in] status Вказівник на структуру зі зчитаними статусами безпеки.
 */
void efuse_security_print_summary(const efuse_security_status_t *status);

/**
 * @brief Безпечний вирівняний запис зашифрованих даних у вказаний розділ Flash-пам'яті.
 *
 * Перевіряє кратність та вирівнювання зсуву й розміру по межі 32 байти (AES-XTS),
 * після чого здійснює запис за допомогою esp_partition_write_raw().
 *
 * @param[in] partition_label Назва (мітка) розділу Flash-пам'яті.
 * @param[in] offset Зсув всередині розділу (має бути кратним 32 байтам).
 * @param[in] data Вказівник на буфер даних для запису.
 * @param[in] size Розмір даних у байтах (має бути кратним 32 байтам).
 * @return esp_err_t ESP_OK у разі успіху, або відповідний код помилки.
 */
esp_err_t efuse_security_write_encrypted_partition(const char *partition_label, size_t offset, const void *data, size_t size);

/**
 * @brief Зчитування даних із розділу Flash-пам'яті через raw API.
 *
 * @param[in] partition_label Назва (мітка) розділу Flash-пам'яті.
 * @param[in] offset Зсув всередині розділу.
 * @param[out] buffer Вказівник на буфер для збереження прочитаних даних.
 * @param[in] size Розмір даних для зчитування в байтах.
 * @return esp_err_t ESP_OK у разі успіху, або відповідний код помилки.
 */
esp_err_t efuse_security_read_encrypted_partition(const char *partition_label, size_t offset, void *buffer, size_t size);

#ifdef __cplusplus
}
#endif

#endif /* EFUSE_FLASH_SECURITY_H */
