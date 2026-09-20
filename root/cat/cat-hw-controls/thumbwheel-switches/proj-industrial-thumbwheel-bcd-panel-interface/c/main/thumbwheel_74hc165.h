#ifndef THUMBWHEEL_74HC165_H
#define THUMBWHEEL_74HC165_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

/// Максимальна кількість 4-бітних декад BCD у каскаді
#define THUMBWHEEL_MAX_DIGITS 8

/**
 * @brief Конфігурація апаратного драйвера 74HC165
 */
typedef struct {
    spi_host_device_t spi_host;   ///< Диспетчер шини SPI (наприклад, SPI2_HOST)
    gpio_num_t pin_pl;            ///< Вивід Parallel Load (PL / Latch, активний низький)
    gpio_num_t pin_miso;          ///< Вивід Serial Data (Q7 останнього регістра 74HC165)
    gpio_num_t pin_sclk;          ///< Вивід Serial Clock (CP)
    uint8_t num_digits;           ///< Кількість підключених 4-бітних BCD декад
    uint32_t debounce_ms;         ///< Інтервал фіксації брязкоту контактів у мс
    bool active_low;              ///< Прапорець інверсної (active-low) схемотехніки
} thumbwheel_config_t;

/**
 * @brief Структура збереження декодованих даних BCD
 */
typedef struct {
    uint8_t digits[THUMBWHEEL_MAX_DIGITS]; ///< Декодовані двійково-десяткові цифри (0..9)
    uint8_t num_digits;                     ///< Фактична кількість декад
    uint32_t raw_value;                     ///< Підсумкове обчислене десяткове значення
    bool valid;                             ///< Прапорець валідності кадру (відсутність 10..15)
} thumbwheel_data_t;

/**
 * @brief Ініціалізація периферійних модулів SPI та GPIO для керування 74HC165
 * @param config Вказівник на структуру конфігурації
 * @return ESP_OK у разі успішного налаштування
 */
esp_err_t thumbwheel_init(const thumbwheel_config_t *config);

/**
 * @brief Виконання защелкування PL та зчитування BCD кадру з каскаду 74HC165
 * @param out_data Вказівник на структуру для повернення результатів
 * @return ESP_OK при успішній передачі по SPI
 */
esp_err_t thumbwheel_read(thumbwheel_data_t *out_data);

#ifdef __cplusplus
}
#endif

#endif // THUMBWHEEL_74HC165_H
