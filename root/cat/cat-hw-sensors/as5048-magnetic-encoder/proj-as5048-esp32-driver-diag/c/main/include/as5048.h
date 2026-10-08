#ifndef AS5048_H
#define AS5048_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Адреси 16-бітних SPI-регістрів магнітного енкодера AS5048.
 */
#define AS5048_REG_NOP          0x0000  /*!< Регістр NOP (Без операції) / Даммі-запит */
#define AS5048_REG_ERRFL        0x0001  /*!< Регістр помилок (Clear Error Flag) */
#define AS5048_REG_PROG         0x0003  /*!< Регістр керування програмуванням OTP */
#define AS5048_REG_AGC_DIAG     0x3FFE  /*!< Регістр діагностики магнітного поля та рівня AGC */
#define AS5048_REG_ANGLE        0x3FFF  /*!< Регістр 14-бітного кутового положення */
#define AS5048_REG_MAGNITUDE    0x3FFD  /*!< Регістр величини магнітного вектора */

/**
 * @brief Маски бітів 16-бітного SPI кадру.
 */
#define AS5048_FRAME_PARITY_BIT 0x8000  /*!< Біт 15: Навітьна парність (Even Parity) */
#define AS5048_FRAME_READ_BIT   0x4000  /*!< Біт 14: 1 = Читання, 0 = Запис (у командному кадрі) */
#define AS5048_FRAME_EF_BIT     0x4000  /*!< Біт 14: Прапорець помилки кадру (Error Flag, у відповіді) */
#define AS5048_DATA_MASK        0x3FFF  /*!< Біти 13..0: 14-бітне корисне навантаження */

/**
 * @brief Маски прапорців регістру помилок ERRFL (0x0001).
 */
#define AS5048_ERR_FRAMING      (1 << 0) /*!< Помилка кадрування (некоректна кількість тактових імпульсів) */
#define AS5048_ERR_INVALID_CMD  (1 << 1) /*!< Некоректна команда або недопустима адреса регістру */
#define AS5048_ERR_PARITY       (1 << 2) /*!< Помилка парності переданої команди */

/**
 * @brief Маски бітів регістру AGC та діагностики (0x3FFE).
 */
#define AS5048_AGC_MASK         0x00FF  /*!< Біти 7..0: Рівень автоматичного регулювання підсилення (AGC, 0..255) */
#define AS5048_DIAG_OCF         (1 << 8)  /*!< Біт 8: Offset Compensation Finished (1 = CORDIC завершено) */
#define AS5048_DIAG_COF         (1 << 9)  /*!< Біт 9: CORDIC Overflow (1 = переповнення обчислювача) */
#define AS5048_DIAG_MAGL        (1 << 10) /*!< Біт 10: Магнітне поле занадто слабке (MAGL) */
#define AS5048_DIAG_MAGH        (1 << 11) /*!< Біт 11: Магнітне поле занадто сильне (MAGH) */

/**
 * @brief Роздільна здатність енкодера AS5048 (14 біт = 16384 відліки).
 */
#define AS5048_MAX_RAW_ANGLE    16384

/**
 * @brief Структура для збереження діагностичного стану енкодера.
 */
typedef struct {
    uint8_t agc_val;   /*!< Поточне значення AGC підсилення (0..255, оптимальне ~128) */
    bool ocf;          /*!< Готовність компенсації зсуву (Offset Compensation Finished) */
    bool cof;          /*!< Переповнення обчислювача CORDIC (CORDIC Overflow) */
    bool magh;         /*!< Прапорець занадто сильного магнітного поля (Magnet High) */
    bool magl;         /*!< Прапорець занадто слабкого магнітного поля (Magnet Low) */
} as5048_diag_status_t;

/**
 * @brief Структура конфігурації для ініціалізації AS5048.
 */
typedef struct {
    spi_host_device_t spi_host; /*!< SPI модуль ESP32 (наприклад, SPI2_HOST) */
    gpio_num_t cs_io_num;       /*!< Номер GPIO для виводу Chip Select */
    int clock_speed_hz;         /*!< Частота SPI годинника в Гц (наприклад, 1000000) */
    uint16_t zero_offset;       /*!< Початкове значення програмного зсуву нуля */
} as5048_config_t;

/**
 * @brief Непрозорий дескриптор контексту пристрою AS5048.
 */
typedef struct as5048_dev_s *as5048_handle_t;

/**
 * @brief Обчислення біта парності (even parity) для 16-бітного кадру.
 *
 * @param value 16-бітне слово, для 15 молодших бітів якого вираховується парність.
 * @return uint16_t Повертає 0x8000 якщо кількість одиниць непарна, або 0x0000.
 */
uint16_t as5048_calculate_parity(uint16_t value);

/**
 * @brief Ініціалізація драйвера AS5048 та додавання пристрою до SPI-шини ESP32.
 *
 * @param config Вказівник на структуру конфігурації.
 * @param out_handle Вказівник для повернення створеного дескриптора.
 * @return esp_err_t ESP_OK у разі успіху, або код помилки ESP-IDF.
 */
esp_err_t as5048_init(const as5048_config_t *config, as5048_handle_t *out_handle);

/**
 * @brief Деініціалізація драйвера AS5048 та звільнення ресурсів SPI.
 *
 * @param handle Дескриптор пристрою.
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_deinit(as5048_handle_t handle);

/**
 * @brief Зчитування необробленого (raw) 14-бітного значення кута з регістра ANGLE.
 *
 * @param handle Дескриптор пристрою.
 * @param out_raw_angle Вказівник для збереження 14-бітного значення (0..16383).
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_read_raw_angle(as5048_handle_t handle, uint16_t *out_raw_angle);

/**
 * @brief Зчитування поточного кута у градусах (з урахуванням компенсації нуля).
 *
 * @param handle Дескриптор пристрою.
 * @param out_degrees Вказівник для збереження значення кута в градусах (0.0 .. 360.0).
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_read_angle(as5048_handle_t handle, float *out_degrees);

/**
 * @brief Встановлення значення програмного зсуву нульової позиції.
 *
 * @param handle Дескриптор пристрою.
 * @param zero_offset Значення зсуву (0..16383).
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_set_zero_offset(as5048_handle_t handle, uint16_t zero_offset);

/**
 * @brief Програмне калібрування нуля: зчитує поточний кут і встановлює його як zero offset.
 *
 * @param handle Дескриптор пристрою.
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_calibrate_zero(as5048_handle_t handle);

/**
 * @brief Отримання діагностичного стану AGC та прапорців поля з регістра 0x3FFE.
 *
 * @param handle Дескриптор пристрою.
 * @param out_diag Вказівник на структуру діагностики.
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_get_diagnostics(as5048_handle_t handle, as5048_diag_status_t *out_diag);

/**
 * @brief Зчитування та скидання прапорців помилок з регістра ERRFL (0x0001).
 *
 * @param handle Дескриптор пристрою.
 * @param out_error_flags Вказівник на змінну для збереження прапорців (AS5048_ERR_*).
 * @return esp_err_t ESP_OK при успіху.
 */
esp_err_t as5048_read_error(as5048_handle_t handle, uint16_t *out_error_flags);

/**
 * @brief Конвертація 14-бітного необробленого відліку у градуси.
 *
 * @param raw_angle Значення кута (0..16383).
 * @return float Градуси від 0.0 до 360.0.
 */
float as5048_raw_to_degrees(uint16_t raw_angle);

#ifdef __cplusplus
}
#endif

#endif /* AS5048_H */
