#ifndef BISSC_ENCODER_H
#define BISSC_ENCODER_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура конфігурації апаратної шини для енкодера BiSS-C
 */
typedef struct {
    spi_host_device_t spi_host;   ///< Диспетчер шини SPI (наприклад, SPI2_HOST)
    gpio_num_t pin_ma;            ///< Вивід тактування Master Ack (MA / SCLK)
    gpio_num_t pin_slo;           ///< Вивід даних Slave Out (SLO / MISO)
    uint32_t clock_speed_hz;      ///< Частота тактування MA в Гц (наприклад, 2000000 для 2 МГц)
    uint8_t data_bits;            ///< Кількість бітів кутової позиції (наприклад, 18 або 24 біти)
    bool is_gray_code;            ///< Прапорець кодування позиції в коді Ґрея
} bissc_config_t;

/**
 * @brief Структура декодованого кадру даних BiSS-C
 */
typedef struct {
    uint32_t raw_position;        ///< Сира позиція з кадру (до конверсії коду Ґрея)
    uint32_t position;            ///< Декодована двійкова позиція
    float angle_degrees;          ///< Кут у градусах (0.0 ... 360.0)
    bool error_flag;              ///< Апаратна помилка енкодера E (true — помилка присутня)
    bool warning_flag;            ///< Попередження енкодера W (true — попередження присутнє)
    uint8_t crc_received;         ///< Прийнята з кадру 6-бітна контрольна сума CRC
    uint8_t crc_calculated;       ///< Обчислена 6-бітна контрольна сума CRC
    bool crc_valid;               ///< Прапорець успішної верифікації CRC
} bissc_frame_t;

/**
 * @brief Перетворення значення коду Ґрея у двійковий формат
 * @param gray Значення в коді Ґрея
 * @return Двійкове еквівалентне число
 */
uint32_t bissc_gray_to_binary(uint32_t gray);

/**
 * @brief Обчислення 6-бітної контрольної суми CRC-6 (поліном 0x43) для кадру BiSS-C
 * @param data_val Значення даних (позиція + біти E та W)
 * @param num_bits Кількість бітів у вибірці
 * @return 6-бітна контрольна сума
 */
uint8_t bissc_calculate_crc6(uint64_t data_val, uint8_t num_bits);

/**
 * @brief Ініціалізація периферії SPI для роботи з енкодером BiSS-C
 * @param config Посилання на структуру конфігурації
 * @return ESP_OK у разі успішного налаштування
 */
esp_err_t bissc_encoder_init(const bissc_config_t *config);

/**
 * @brief Зчитування та розбір кадру даних із BiSS-C енкодера
 * @param out_frame Посилання на структуру для збереження результатів
 * @return ESP_OK у разі успішного зчитування
 */
esp_err_t bissc_encoder_read_frame(bissc_frame_t *out_frame);

#ifdef __cplusplus
}
#endif

#endif // BISSC_ENCODER_H
