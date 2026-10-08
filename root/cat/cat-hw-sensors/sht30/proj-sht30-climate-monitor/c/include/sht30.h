#ifndef SHT30_H
#define SHT30_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "i2c_bus.h"

/**
 * @file sht30.h
 * @brief Оголошення C-інтерфейсу модульного драйвера цифрового давача SHT30 (I2C).
 */

/**
 * @brief 7-бітні I2C адреси сенсора SHT30.
 */
#define SHT30_I2C_ADDR_A 0x44 /**< Вивід ADDR підключений до GND (за замовчуванням) */
#define SHT30_I2C_ADDR_B 0x45 /**< Вивід ADDR підключений до VDD */

/**
 * @brief Перелічення 16-бітних команд I2C для керування SHT30.
 */
typedef enum {
    /* Однократне вимірювання з розтягуванням тактового сигналу (Clock Stretching) */
    SHT30_CMD_MEAS_CLOCKSTR_HIGH   = 0x2C06, /**< Висока точність */
    SHT30_CMD_MEAS_CLOCKSTR_MEDIUM = 0x2D0D, /**< Середня точність */
    SHT30_CMD_MEAS_CLOCKSTR_LOW    = 0x2E0E, /**< Низька точність */

    /* Однократне вимірювання без розтягування тактового сигналу (Polling) */
    SHT30_CMD_MEAS_POLL_HIGH       = 0x2400, /**< Висока точність */
    SHT30_CMD_MEAS_POLL_MEDIUM     = 0x240B, /**< Середня точність */
    SHT30_CMD_MEAS_POLL_LOW        = 0x2416, /**< Низька точність */

    /* Періодичний режим вимірювань (Periodic Mode) */
    SHT30_CMD_PERIODIC_1MPS_HIGH   = 0x2130, /**< 1 вимірювання на секунду, висока точність */
    SHT30_CMD_FETCH_DATA           = 0xE000, /**< Зчитування останнього вимірювання з буфера */
    SHT30_CMD_BREAK                = 0x3093, /**< Зупинка періодичного режиму */

    /* Службові та апаратні команди */
    SHT30_CMD_SOFT_RESET           = 0x30A2, /**< Програмне скидання сенсора */
    SHT30_CMD_HEATER_ENABLE        = 0x306D, /**< Увімкнення підігрівача */
    SHT30_CMD_HEATER_DISABLE       = 0x3066, /**< Вимкнення підігрівача */
    SHT30_CMD_READ_STATUS          = 0xF32D, /**< Читання регістру статусу */
    SHT30_CMD_CLEAR_STATUS         = 0x3041  /**< Очищення прапорців статусу */
} sht30_cmd_t;

/**
 * @brief Рівні точності / повторюваності вимірювань SHT30.
 */
typedef enum {
    SHT30_REPEATABILITY_HIGH   = 0, /**< Висока точність (тривалість ~15 мс) */
    SHT30_REPEATABILITY_MEDIUM = 1, /**< Середня точність (тривалість ~6 мс) */
    SHT30_REPEATABILITY_LOW    = 2  /**< Низька точність (тривалість ~4 мс) */
} sht30_repeatability_t;

/**
 * @brief Коди результатів та помилок виконання функцій драйвера SHT30.
 */
typedef enum {
    SHT30_OK                     =  0, /**< Успішне виконання операції */
    SHT30_ERR_INVALID_ARG        = -1, /**< Некоректні вхідні аргументи */
    SHT30_ERR_I2C_BUS            = -2, /**< Збій транзакції на шині I2C */
    SHT30_ERR_CRC_TEMP           = -3, /**< Помилка CRC-8 вибірки температури */
    SHT30_ERR_CRC_HUMIDITY       = -4, /**< Помилка CRC-8 вибірки вологості */
    SHT30_ERR_TIMEOUT            = -5, /**< Перевищено тайм-аут очікування */
    SHT30_ERR_DEW_POINT_INVALID  = -6  /**< Помилка розрахунку точки роси */
} sht30_err_t;

/**
 * @brief Структура вибірок параметрів довкілля.
 */
typedef struct {
    float temperature_c;    /**< Температура в градусах Цельсія */
    float humidity_percent; /**< Відносна вологість у відсотках (0..100%) */
    float dew_point_c;      /**< Розрахована точка роси в градусах Цельсія */
    bool is_crc_valid;      /**< Прапорець цілісності даних CRC-8 */
} sht30_data_t;

/**
 * @brief Розшифрований стан регістру статусу SHT30.
 */
typedef struct {
    bool checksum_failed;  /**< Помилка контрольної суми останньої команди */
    bool command_failed;   /**< Відхилення останньої команди сенсором */
    bool system_reset;     /**< Стан виконанного скидання (Soft/Power Reset) */
    bool heater_active;    /**< Стан вбудованого нагрівача (true - увімкнений) */
    bool alert_pending;    /**< Прапорець активного сигналу тривоги */
} sht30_status_t;

/**
 * @brief Структура конфігурації та дескриптора пристрою SHT30.
 */
typedef struct {
    uint8_t i2c_address;                /**< I2C адреса (0x44 або 0x45) */
    bool use_clock_stretching;          /**< Дозвіл Clock Stretching */
    sht30_repeatability_t repeatability;/**< Режим точності вимірювання */
    uint32_t timeout_ms;                /**< Тайм-аут шинного обміну в мс */
    void (*delay_ms)(uint32_t ms);      /**< Вказівник на функцію системної затримки */
} sht30_t;

/* --- Прототипи функцій драйвера --- */

/**
 * @brief Ініціалізація дескриптора драйвера SHT30.
 */
sht30_err_t sht30_init(sht30_t *dev, uint8_t i2c_addr, void (*delay_fn)(uint32_t ms));

/**
 * @brief Обчислення контрольної суми CRC-8 (поліном 0x31, початковий стан 0xFF).
 */
uint8_t sht30_calc_crc8(const uint8_t *data);

/**
 * @brief Зчитування температури, вологості та обчислення точки роси з перевіркою CRC-8.
 */
sht30_err_t sht30_read_single_shot(sht30_t *dev, sht30_data_t *data);

/**
 * @brief Виконання програмного скиду сенсора (Soft Reset).
 */
sht30_err_t sht30_soft_reset(sht30_t *dev);

/**
 * @brief Управління вбудованим елементом нагрівання для сушки від конденсату.
 */
sht30_err_t sht30_set_heater(sht30_t *dev, bool enable);

/**
 * @brief Зчитування та декодування регістру статусу SHT30.
 */
sht30_err_t sht30_read_status(sht30_t *dev, sht30_status_t *status);

/**
 * @brief Очищення прапорців у регістрі статусу SHT30.
 */
sht30_err_t sht30_clear_status(sht30_t *dev);

/**
 * @brief Розрахунок точки роси за формулою Магнуса.
 */
sht30_err_t sht30_calculate_dew_point(float temp_c, float humidity_percent, float *dew_point_c);

#endif /* SHT30_H */
