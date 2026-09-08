#ifndef INA219_H
#define INA219_H

#include <stdint.h>
#include <stdbool.h>

#define INA219_I2C_ADDR_DEFAULT   0x40

/* Адреси внутрішніх регістрів INA219 */
#define INA219_REG_CONFIG         0x00
#define INA219_REG_SHUNTVOLTAGE   0x01
#define INA219_REG_BUSVOLTAGE     0x02
#define INA219_REG_POWER          0x03
#define INA219_REG_CURRENT        0x04
#define INA219_REG_CALIBRATION    0x05

/* Структура результатів вимірювань */
typedef struct {
    int32_t bus_voltage_mv;   /* Напруга шини в мілівольтах */
    int32_t shunt_voltage_uv; /* Спад напруги на шунті в мікровольтах */
    int32_t current_ma;       /* Струм навантаження в міліамперах */
    int32_t power_mw;         /* Споживана потужність у міліватах */
} Ina219Telemetry;

/* Структура порогових захисних лімітів */
typedef struct {
    int32_t max_voltage_mv;   /* Поріг OVP (захист від перенапруги) */
    int32_t min_voltage_mv;   /* Поріг UVP (захист від просідання) */
    int32_t max_current_ma;   /* Поріг OCP (захист від перевантаження/КЗ) */
} Ina219Limits;

/**
 * @brief Ініціалізація та калібрування сенсора INA219 на шунт 0.1 Ом.
 * @param i2c_addr 7-бітний адрес I2C (за замовчуванням 0x40).
 * @return true при успішній відповіді пристрою; false у разі помилки зв'язку.
 */
bool ina219_init(uint8_t i2c_addr);

/**
 * @brief Зчитування повного пакета електричної телеметрії.
 * @param[out] data Вказівник на структуру для збереження результатів.
 * @return true при коректному зчитуванні.
 */
bool ina219_read_data(Ina219Telemetry *data);

/**
 * @brief Перевірка перевищення порогових меж струму й напруги.
 * @param data Поточні зняті покази.
 * @param limits Задані граничні параметри.
 * @return true якщо параметри в безпечній зоні; false при аварії.
 */
bool ina219_check_safety(const Ina219Telemetry *data, const Ina219Limits *limits);

#endif /* INA219_H */
