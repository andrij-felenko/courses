#ifndef BME280_H
#define BME280_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "i2c_hal.h"

/**
 * @file bme280.h
 * @brief Оголошення C-інтерфейсу низькорівневого драйвера Bosch BME280.
 * 
 * Включає адреси реєстрів, маски режимів (Sleep, Forced), коефіцієнти оверсемплінгу,
 * структури калібрувальних параметрів bme280_calib_t, сирих відліків bme280_raw_t,
 * фізичних даних bme280_data_t, дескриптора bme280_t та прототипи функцій компенсації.
 */

/* I2C адреси пристрою BME280 */
#define BME280_I2C_ADDR_PRIM        0x76  /*!< Адреса за замовчуванням (SDO підключено до GND) */
#define BME280_I2C_ADDR_SEC         0x77  /*!< Альтернативна адреса (SDO підключено до VDDIO) */

/* Адреси реєстрів BME280 */
#define BME280_REG_DIG_T1_LSB       0x88  /*!< Початок блоку 1 калібрувальних коефіцієнтів NVM (0x88..0xA1) */
#define BME280_REG_CHIP_ID          0xD0  /*!< Регістр ідентифікатора чипа (очікуване значення 0x60) */
#define BME280_REG_RESET            0xE0  /*!< Регістр програмного скидання (команда 0xB6) */
#define BME280_REG_DIG_H2_LSB       0xE1  /*!< Початок блоку 2 калібрувальних коефіцієнтів NVM (0xE1..0xE7) */
#define BME280_REG_CTRL_HUM         0xF2  /*!< Контроль оверсемплінгу вологості (osrs_h) */
#define BME280_REG_STATUS           0xF3  /*!< Статус виконання вимірювання та оновлення NVM */
#define BME280_REG_CTRL_MEAS        0xF4  /*!< Контроль оверсемплінгу T/P та вибір режиму роботи */
#define BME280_REG_CONFIG           0xF5  /*!< Конфігурація періоду очікування та IIR-фільтра */
#define BME280_REG_PRESS_MSB        0xF7  /*!< Початок 8-байтного блоку сирих вибірок АЦП (0xF7..0xFE) */

/* Константні значення та бітові маски */
#define BME280_CHIP_ID_VALUE        0x60  /*!< Еталонне значення Chip ID BME280 */
#define BME280_RESET_CMD            0xB6  /*!< Значення для програмного скидання сенсора */
#define BME280_STATUS_MEASURING_MSK 0x08  /*!< Біт 3 регістру status: 1 - вимірювання триває */
#define BME280_STATUS_IM_UPDATE_MSK 0x01  /*!< Біт 0 регістру status: 1 - копіювання NVM давача */

/**
 * @brief Коди помилок драйвера BME280
 */
typedef enum {
    BME280_OK                   =  0,  /*!< Операція успішна */
    BME280_ERR_NULL_PTR         = -1,  /*!< Передано нульовий вказівник */
    BME280_ERR_INVALID_CHIP_ID  = -2,  /*!< Невідповідність Chip ID (не 0x60) */
    BME280_ERR_I2C              = -3,  /*!< Помилка обміну по шині I2C */
    BME280_ERR_TIMEOUT          = -4,  /*!< Перевищення часу очікування готовності */
    BME280_ERR_INVALID_PARAM    = -5   /*!< Некоректне значення параметрів */
} bme280_err_t;

/**
 * @brief Коефіцієнти оверсемплінгу АЦП
 */
typedef enum {
    BME280_OVERSAMPLING_SKIPPED = 0,  /*!< Вимірювання вимкнено (повертає 0) */
    BME280_OVERSAMPLING_1X      = 1,  /*!< Оверсемплінг x1 */
    BME280_OVERSAMPLING_2X      = 2,  /*!< Оверсемплінг x2 */
    BME280_OVERSAMPLING_4X      = 3,  /*!< Оверсемплінг x4 */
    BME280_OVERSAMPLING_8X      = 4,  /*!< Оверсемплінг x8 */
    BME280_OVERSAMPLING_16X     = 5   /*!< Оверсемплінг x16 */
} bme280_oversampling_t;

/**
 * @brief Режими роботи давача BME280
 */
typedef enum {
    BME280_MODE_SLEEP  = 0,  /*!< Режим сну: мінімальне енергоспоживання */
    BME280_MODE_FORCED = 1,  /*!< Режим поодинокого вимірювання (Forced Mode) */
    BME280_MODE_NORMAL = 3   /*!< Неперервний режим регулярних вимірювань */
} bme280_mode_t;

/**
 * @brief Структура фабричних калібрувальних коефіцієнтів з NVM-пам'яті давача
 */
typedef struct {
    uint16_t dig_T1;  /*!< Калібрування температури T1 */
    int16_t  dig_T2;  /*!< Калібрування температури T2 */
    int16_t  dig_T3;  /*!< Калібрування температури T3 */
    uint16_t dig_P1;  /*!< Калібрування тиску P1 */
    int16_t  dig_P2;  /*!< Калібрування тиску P2 */
    int16_t  dig_P3;  /*!< Калібрування тиску P3 */
    int16_t  dig_P4;  /*!< Калібрування тиску P4 */
    int16_t  dig_P5;  /*!< Калібрування тиску P5 */
    int16_t  dig_P6;  /*!< Калібрування тиску P6 */
    int16_t  dig_P7;  /*!< Калібрування тиску P7 */
    int16_t  dig_P8;  /*!< Калібрування тиску P8 */
    int16_t  dig_P9;  /*!< Калібрування тиску P9 */
    uint8_t  dig_H1;  /*!< Калібрування вологості H1 */
    int16_t  dig_H2;  /*!< Калібрування вологості H2 */
    uint8_t  dig_H3;  /*!< Калібрування вологості H3 */
    int16_t  dig_H4;  /*!< Калібрування вологості H4 */
    int16_t  dig_H5;  /*!< Калібрування вологості H5 */
    int8_t   dig_H6;  /*!< Калібрування вологості H6 */
} bme280_calib_t;

/**
 * @brief Сирі некомпенсовані відліки АЦП з давача
 */
typedef struct {
    uint32_t raw_temperature;  /*!< 20-бітний відлік АЦП температури */
    uint32_t raw_pressure;     /*!< 20-бітний відлік АЦП тиску */
    uint32_t raw_humidity;     /*!< 16-бітний відлік АЦП вологості */
} bme280_raw_t;

/**
 * @brief Кориговані (компенсовані) фізичні величини довкілля
 */
typedef struct {
    int32_t  temperature_degc_x100;  /*!< Температура в сотнях градусів Цельсія (2345 = 23.45 °C) */
    uint32_t pressure_pa;            /*!< Атмосферний тиск у Паскалях (Па) */
    uint32_t humidity_rh_x1024;      /*!< Відносна вологість (%RH * 1024) */
    float    temperature_degc;       /*!< Температура в градусах Цельсія (°C) */
    float    pressure_hpa;           /*!< Атмосферний тиск у гектопаскалях (гПа) */
    float    humidity_rh;            /*!< Відносна вологість у відсотках (%RH) */
} bme280_data_t;

/**
 * @brief Дескриптор екземпляра давача BME280
 */
typedef struct {
    uint8_t               i2c_addr;  /*!< 7-бітна I2C адреса (0x76 або 0x77) */
    bme280_calib_t        calib;     /*!< Фабричні калібрувальні коефіцієнти */
    int32_t               t_fine;    /*!< Проміжна температура для розрахунку P та H */
    bme280_oversampling_t osrs_t;    /*!< Налаштування оверсемплінгу температури */
    bme280_oversampling_t osrs_p;    /*!< Налаштування оверсемплінгу тиску */
    bme280_oversampling_t osrs_h;    /*!< Налаштування оверсемплінгу вологості */
} bme280_t;

/* --- Прототипи функцій драйвера BME280 --- */

/**
 * @brief Ініціалізація драйвера BME280, перевірка Chip ID та зчитування NVM-калібрування.
 * @param dev Вказівник на дескриптор давача.
 * @param i2c_addr 7-бітна I2C адреса (BME280_I2C_ADDR_PRIM / BME280_I2C_ADDR_SEC).
 * @return BME280_OK у разі успіху або відповідний код помилки.
 */
bme280_err_t bme280_init(bme280_t *dev, uint8_t i2c_addr);

/**
 * @brief Виконання програмного скидання давача BME280.
 * @param dev Вказівник на дескриптор давача.
 * @return BME280_OK у разі успішного скидання.
 */
bme280_err_t bme280_soft_reset(bme280_t *dev);

/**
 * @brief Зчитування та десеріалізація масивів калібрувальних коефіцієнтів з NVM.
 * @param dev Вказівник на дескриптор давача.
 * @return BME280_OK при коректному зчитуванні всіх параметрів.
 */
bme280_err_t bme280_read_calibration(bme280_t *dev);

/**
 * @brief Конфігурування коефіцієнтів оверсемплінгу для вимірювальних каналів.
 * @param dev Вказівник на дескриптор давача.
 * @param osrs_t Кратність оверсемплінгу температури.
 * @param osrs_p Кратність оверсемплінгу тиску.
 * @param osrs_h Кратність оверсемплінгу вологості.
 * @return BME280_OK при збереженні конфігурації.
 */
bme280_err_t bme280_set_oversampling(bme280_t *dev,
                                    bme280_oversampling_t osrs_t,
                                    bme280_oversampling_t osrs_p,
                                    bme280_oversampling_t osrs_h);

/**
 * @brief Запуск поодинокого вимірювання в режимі Forced Mode.
 * @param dev Вказівник на дескриптор давача.
 * @return BME280_OK після запису керуючих регістрів.
 */
bme280_err_t bme280_trigger_forced_measurement(bme280_t *dev);

/**
 * @brief Перевірка прапорця виконання вимірювання в регістрі status.
 * @param dev Вказівник на дескриптор давача.
 * @param is_busy Вказівник для збереження стану (true - замір триває, false - завершено).
 * @return BME280_OK при успішному зчитуванні статусу.
 */
bme280_err_t bme280_is_measuring(bme280_t *dev, bool *is_busy);

/**
 * @brief Пакетне (burst) зчитування 8 байтів сирих вибірок АЦП (0xF7..0xFE).
 * @param dev Вказівник на дескриптор давача.
 * @param raw Вказівник на структуру для збереження некомпенсованих даних.
 * @return BME280_OK у разі успішної I2C-транзакції.
 */
bme280_err_t bme280_read_raw_data(bme280_t *dev, bme280_raw_t *raw);

/**
 * @brief Розрахунок компенсованих фізичних величин за цілочисельними формулами Bosch.
 * @param dev Вказівник на дескриптор давача (містить t_fine та calib).
 * @param raw Вказівник на некомпенсовані сирі відліки АЦП.
 * @param data Вказівник для збереження обчислених фізичних величин.
 * @return BME280_OK у разі успішного розрахунку.
 */
bme280_err_t bme280_compensate_data(bme280_t *dev, const bme280_raw_t *raw, bme280_data_t *data);

/**
 * @brief Повний цикл поодинокого заміру в Forced Mode: тригерування, очікування, зчитування та компенсація.
 * @param dev Вказівник на дескриптор давача.
 * @param data Вказівник для збереження результатів вимірювання.
 * @return BME280_OK при успішному виконанні всього циклу.
 */
bme280_err_t bme280_perform_forced_measurement(bme280_t *dev, bme280_data_t *data);

/**
 * @brief Перетворення коду помилки BME280 у текстовий опис.
 * @param err Код помилки.
 * @return const char* Рядоковий опис українською мовою.
 */
const char* bme280_err_to_str(bme280_err_t err);

#endif /* BME280_H */
