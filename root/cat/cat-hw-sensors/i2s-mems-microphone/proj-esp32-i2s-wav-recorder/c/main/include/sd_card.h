/**
 * @file sd_card.h
 * @brief Оголошення C-інтерфейсу монтування SD-картки у VFS ESP-IDF.
 */

#ifndef SD_CARD_H
#define SD_CARD_H

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "driver/gpio.h"
#include "sdmmc_cmd.h"
#include "esp_vfs_fat.h"

#ifdef __cplusplus
extern "C" {
#endif

/** Типова точка монтування SD-картки у VFS */
#define SD_CARD_MOUNT_POINT "/sdcard"

/** Типові GPIO-піни для підключення SD-картки у режимі SPI */
#define SD_CARD_PIN_MISO GPIO_NUM_19
#define SD_CARD_PIN_MOSI GPIO_NUM_23
#define SD_CARD_PIN_CLK  GPIO_NUM_18
#define SD_CARD_PIN_CS   GPIO_NUM_5

/**
 * @brief Конфігурація підключення SD-картки
 */
typedef struct {
    const char *mount_point;   /**< Точка монтування (наприклад, "/sdcard") */
    gpio_num_t pin_miso;       /**< Пін MISO SPI */
    gpio_num_t pin_mosi;       /**< Пін MOSI SPI */
    gpio_num_t pin_clk;        /**< Пін CLK SPI */
    gpio_num_t pin_cs;         /**< Пін Chip Select CS */
    int max_files;             /**< Максимальна кількість одночасно відкритих файлів */
    size_t format_if_mount_failed; /**< Форматувати якщо монтування невдале (0 = ні, 1 = так) */
} sd_card_config_t;

/**
 * @brief Ініціалізація шини SPI та монтування файлової системи FATFS SD-картки
 *
 * @param[in] config Вказівник на конфігурацію SD-картки
 * @return ESP_OK у разі успішного монтування
 */
esp_err_t sd_card_init(const sd_card_config_t *config);

/**
 * @brief Перевірка статусу монтування SD-картки
 *
 * @return true якщо SD-картка примонтована, інакше false
 */
bool sd_card_is_mounted(void);

/**
 * @brief Отримання обсягу вільного та загального місця на SD-картці
 *
 * @param[out] out_free_bytes Вільне місце у байтах
 * @param[out] out_total_bytes Загальний обсяг у байтах
 * @return ESP_OK у разі успіху
 */
esp_err_t sd_card_get_free_space(uint64_t *out_free_bytes, uint64_t *out_total_bytes);

/**
 * @brief Безаварійне розмонтування SD-картки та звільнення шини SPI
 *
 * @return ESP_OK у разі успіху
 */
esp_err_t sd_card_deinit(void);

#ifdef __cplusplus
}
#endif

#endif /* SD_CARD_H */
